import argparse
import json
import re
from argparse import ArgumentParser
from pathlib import Path
from typing import TypeGuard

import requests
from bs4 import BeautifulSoup, NavigableString, PageElement, Tag
from tqdm import tqdm

_ENTRIES_PER_PAGE = 25


def main() -> None:
    args = create_parser().parse_args()
    result = []

    most_recent_saved_page: int | None = None
    fp = Path("buddhist_centers.json")
    if args.reuse and fp.exists():
        result.extend(json.loads(fp.read_text()))
        if result:
            most_recent_saved_page = result[-1]["page"]

    for page in tqdm(range(args.to_page), unit="page"):
        if most_recent_saved_page is not None and page + 1 <= most_recent_saved_page:
            continue
        offset = page * _ENTRIES_PER_PAGE
        url = f"http://www.buddhanet.info/wbd/country.php?country_id=2&offset={offset}"
        result.extend(scrape_buddhist_centers(url, page_number=page + 1))

    output = json.dumps(result, indent=2)
    fp.write_text(output)


def create_parser() -> argparse.ArgumentParser:
    parser = ArgumentParser()
    parser.add_argument(
        "--to-page",
        type=int,
        # At the time of writing, there were only 2650 centers. So conservatively go up to 3000.
        default=3000 // _ENTRIES_PER_PAGE,
        help="Parse up to and including this page.",
    )
    parser.add_argument(
        "--reuse",
        action="store_true",
        default=False,
        help="If true, reuse results already saved to JSON. Only scrape missing pages.",
    )
    return parser


def scrape_buddhist_centers(
    url: str, *, page_number: int
) -> list[dict[str, str | int]]:
    headers = {
        # Necessary to avoid a 403.
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:91.0) Gecko/20100101 Firefox/91.0"
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    entry_names = soup.find_all("p", class_="entryName")
    entry_details = soup.find_all("p", class_="entryDetail")
    return [
        extract_center_info(name, details, page_number=page_number)
        for name, details in zip(entry_names, entry_details, strict=True)
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
        "Notes and Events:",
        "Main Contact:",
        "Phone:",
        "Spiritual Director:",
        "Teacher:",
        "Teachers:",
        "Tradition:",
        "Website:",
    ]
)


def extract_center_info(
    name_tag: Tag, details_tag: Tag, *, page_number: int
) -> dict[str, str | int]:
    result: dict[str, str | int] = {"name": name_tag.text.strip(), "page": page_number}

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

    # Also check if there is a `<p className="entryDesc">` after, which is used for
    # "Notes and Events".
    _maybe_add_entry_desc(details_tag, result)
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
    text_elements = []
    for v in value_elements:
        if isinstance(v, Tag) and v.name == "a":
            href = v["href"]
            assert isinstance(href, str)
            txt = href.removeprefix("mailto:")
        else:
            txt = v.text
        text_elements.append(txt)

    text = " ".join(text_elements).strip()
    if key == "Address":
        text = _normalize_address(text)

    # Remove extra whitespace and `\xa0` characters in the middle of the string.
    text = re.sub(r"\s*\xa0\s*|\s{2,}", " ", text)
    return text


def _normalize_address(value: str) -> str:
    # Remove 'Mailing:' and everything after it. `re.DOTALL` is because there are sometimes
    # newlines after the `Mailing:`.
    value = re.sub(r"\s*Mailing:.*$", "", value, flags=re.DOTALL)

    # Replace `\r\n` and `\n` with `, `.
    value = re.sub(r"(\r\n|\n)+", ", ", value)

    # Remove 'Physical:' if it's at the beginning of the address
    value = re.sub(r"^\s*Physical:\s*", "", value)

    # Remove trailing whitespace, '\xa0', and 2-letter state code
    value = re.sub(r"\s*\xa0\s*[A-Z]{2}$", "", value)

    # Replace whitespace, '\xa0', and a little more whitespace followed by text. This
    # sometimes separates the street from the city and state. Replace with `, `.
    value = re.sub(r"\s*\xa0\s+(?=\S)", ", ", value)

    # Some previous rules can result in occurrences like `,,`. Ensure it's only ever one comma.
    value = re.sub(r",+", ",", value)

    # Finally, replace multiple blank spaces with only one. Note that this happens at the end
    # because the other replacements are more precise.
    value = re.sub(r"\s+", " ", value)
    return value


def _maybe_add_entry_desc(details_tag: Tag, result: dict[str, str | int]) -> None:
    entry_desc = _find_entry_desc(details_tag)
    if entry_desc is None:
        return

    if "Notes and Events" not in result:
        raise AssertionError(
            f"entryDesc found for the center {result['name']}, but there was no "
            "`Notes and Events` key."
        )
    if notes := result["Notes and Events"] != "":
        raise AssertionError(
            f"entryDesc found for the center {result['name']}, but the 'Notes and Events' key has "
            f"its own text already: {notes}"
        )

    result["Notes and Events"] = entry_desc.get_text(strip=True)


def _find_entry_desc(details_tag: Tag) -> Tag | None:
    current_sibling = details_tag.next_sibling
    while current_sibling is not None:
        if isinstance(current_sibling, Tag):
            if current_sibling.get("class") == ["entryDesc"]:
                return current_sibling
            if current_sibling.name == "hr" or current_sibling.get("class") == [
                "entryName"
            ]:
                return None
        current_sibling = current_sibling.next_sibling
    return None


if __name__ == "__main__":
    main()
