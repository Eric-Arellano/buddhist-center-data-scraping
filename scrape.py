import json
import re
from pathlib import Path
from typing import TypeGuard

import requests
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag
from tqdm import tqdm


def main() -> None:
    result = []
    # At the time of writing, there were only 2650 centers. So conservatively go up to 3000.
    num_pages = 3000 // 25
    for page in tqdm(range(num_pages)):
        offset = page * 25
        url = f"http://www.buddhanet.info/wbd/country.php?country_id=2&offset={offset}"
        result.extend(scrape_buddhist_centers(url))

    output = json.dumps(result, indent=2)
    Path("buddhist_centers.json").write_text(output)


def scrape_buddhist_centers(url: str) -> list[dict[str, str]]:
    headers = {
        # Necessary to avoid a 403.
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    entry_names = soup.find_all("p", class_="entryName")
    entry_details = soup.find_all("p", class_="entryDetail")
    return [
        _extract_center_info(name, details)
        for name, details in zip(entry_names, entry_details)
    ]


_KNOWN_KEY_NAMES = frozenset(
    [
        "Abbot:",
        "Address:",
        "Affiliation:",
        "Community Dharma Leader:",
        "Contact:",
        "E-mail:",
        "Founder:",
        "Main Contact:",
        "Phone:",
        "Spiritual Director:",
        "Teacher:",
        "Teachers:",
        "Tradition:",
        "Website:",
    ]
)


def _extract_center_info(name_tag: Tag, details_tag: Tag) -> dict[str, str]:
    result = {"name": name_tag.text}

    # Algorithm: Every key is a strong element in the form `Key:`, followed by a value,
    # and ending in a `<br>` or `None` because the details have ended. So, process each
    # strong-element one-at-a-time to fill in the details.
    for strong_element in details_tag.find_all(["strong"]):
        key_and_value_elements = _determine_key_and_value_elements(strong_element)
        if not key_and_value_elements:
            continue
        key, value_elements = key_and_value_elements
        val = _normalize_value(value_elements, key=key)
        # Sometimes there are duplicate keys; if so, combine.
        result[key] = f"{result[key]}, {val}" if key in result else val

    return result


def _determine_key_and_value_elements(
    strong_element: Tag,
) -> tuple[str, list[Tag | NavigableString]] | None:
    # `Find on:` is broken and not useful.
    if strong_element.text == "Find on:":
        return None

    # Strong elements can be included in the value for a key. We can skip those here because
    # they will already be handled by looking at the key's `next_sibling`.
    if not any(strong_element.text.startswith(k) for k in _KNOWN_KEY_NAMES):
        return None

    key, key_value_text = strong_element.text.split(":", maxsplit=1)
    value_elements: list[Tag | NavigableString] = [NavigableString(key_value_text)]

    def is_valid_element(element: PageElement) -> TypeGuard[Tag | NavigableString]:
        return isinstance(element, (Tag, NavigableString))

    current_value = strong_element.next_sibling
    while (
        current_value is not None
        and is_valid_element(current_value)
        and current_value.name != "br"
    ):
        if not is_valid_element(current_value):
            raise AssertionError(
                f"Unexpected element as sibling to the key `{key}`: "
                f"{current_value} (type {type(current_value)})"
            )
        value_elements.append(current_value)
        current_value = current_value.next_sibling

    return key, value_elements


def _normalize_value(value_elements: list[Tag | NavigableString], *, key: str) -> str:
    text = " ".join(v.text.strip() for v in value_elements).strip()
    if key == "Address":
        text = _normalize_address(text)
    return text


def _normalize_address(value: str) -> str:
    # Remove 'Mailing:' and everything after it. `re.DOTALL` is because there are sometimes
    # newlines after the `Mailing:`.
    value = re.sub(r"\s*Mailing:.*$", "", value, flags=re.DOTALL)

    # Replace '\n' with ', '
    value = re.sub(r"\n", ", ", value)

    # Remove 'Physical:' if it's at the beginning of the address
    value = re.sub(r"^\s*Physical:\s*", "", value)

    # Remove trailing whitespace, '\xa0', and 2-letter state code
    value = re.sub(r"\s*\xa0\s*[A-Z]{2}$", "", value)

    # Replace whitespace, '\xa0', and a little more whitespace followed by text with ', '
    value = re.sub(r"\s*\xa0\s+(?=\S)", ", ", value)

    return value


if __name__ == "__main__":
    main()
