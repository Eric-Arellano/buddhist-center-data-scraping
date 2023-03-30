import json
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup, Tag
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


def _extract_center_info(name_tag: Tag, details_tag: Tag) -> dict[str, str]:
    result = {"name": name_tag.text}
    details = details_tag.find_all(["strong", "br"])

    key = None
    for detail in details:
        if detail.name == "strong":
            if detail.text == "Find on:":
                continue
            key = detail.text.rstrip(":")
        elif key and detail.name == "br":
            value = detail.previous_sibling
            if value is None or value.name == "br":
                continue
            if value.name in ("a", "i", "em", "strong", "u"):
                value = value.text
            value = value.strip()
            if key == "Address":
                value = _normalize_address(value)
            result[key] = value.strip()
            key = None
    return result


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
