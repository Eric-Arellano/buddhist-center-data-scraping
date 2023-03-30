from bs4 import BeautifulSoup, Tag

from scrape import _extract_center_info


def create_tags(name: str, details_html: str) -> tuple[Tag, Tag]:
    name_html = f'<p class="entryName">{name}</p>'

    def get_tag(html: str) -> Tag:
        return BeautifulSoup(html, "html.parser").p

    return get_tag(name_html), get_tag(details_html)


def test_basic() -> None:
    """No values with wrapping elements like `<em>` and no multiline values."""
    tags = create_tags(
        "96th Street Sangha",
        """<p class="entryDetail">
<strong>Address:</strong> 275 W. 96th Street, #4C New York, NY 10025                   &nbsp;  NY <br>
<strong>Tradition:</strong> Mahayana, Zen/Pureland<br>
<strong>Affiliation:</strong> Higashi Honganji<br>
<strong>Phone:</strong> (212) 749-1127<br> 
<strong>E-mail:</strong> <a href="mailto:gyobun@aol.com">gyobun@aol.com</a><br>
<strong>Find on:</strong> <a href="http://mapof.it/275 W. 96th Street, #4C New York, NY 10025                      New York" target="_blank"><img align="absmiddle" src="images/map.gif" border="0" style="margin-top:2px"></a><br>
<strong>Main Contact:</strong> T. Davis &nbsp;<br>
<strong>Spiritual Director:</strong> Rev. Thulani Davis &nbsp;<br>
</p>""",
    )
    assert _extract_center_info(*tags) == {
        "name": "96th Street Sangha",
        # TODO: process this
        "Address": "275 W. 96th Street, #4C New York, NY 10025                   \xa0  NY",
        "Tradition": "Mahayana, Zen/Pureland",
        "Affiliation": "Higashi Honganji",
        "Phone": "(212) 749-1127",
        "E-mail": "gyobun@aol.com",
        "Main Contact": "T. Davis",
        "Spiritual Director": "Rev. Thulani Davis",
    }
