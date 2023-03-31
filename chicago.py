import json
from pathlib import Path


def main() -> None:
    all_centers = json.loads(Path("buddhist_centers.json").read_text())
    result = [
        center
        for center in all_centers
        if (
            any(kw in center["name"] for kw in _KEYWORDS)
            or any(kw in center.get("address", "") for kw in _KEYWORDS)
        )
    ]
    Path("chicago_centers.json").write_text(json.dumps(result, indent=2))


_KEYWORDS = frozenset(["IL", "Illinois", "Chi", "Chicago"])


if __name__ == "__main__":
    main()
