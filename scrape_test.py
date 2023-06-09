import pytest
from bs4 import BeautifulSoup, Tag

from scrape import extract_center_info


def create_tags(name: str, details_html: str) -> tuple[Tag, Tag]:
    name_html = f'<p class="entryName">{name}</p>'

    def get_tag(html: str) -> Tag:
        res = BeautifulSoup(html, "html.parser").p
        assert res is not None
        return res

    return get_tag(name_html), get_tag(details_html)


def test_basic() -> None:
    tags = create_tags(
        " Accidental Buddhist Sangha",
        """<p class="entryDetail">
<strong>Address:</strong>    &nbsp;  IL <br>
<strong>Tradition:</strong> Mahayana, Zen Buddhist Master Thich Nhat Hahn<br>
<strong>Affiliation:</strong> Community of Mindful Living/Order of Interbeing    <br>
<strong>Phone:</strong> (630) 375-0881<br> 
<strong>E-mail:</strong> <a href="mailto:jackhat1@aol.com">jackhat1@aol.com</a><br>
<strong>Find on:</strong> <a href="http://mapof.it/      Illinois" target="_blank"><img align="absmiddle" src="images/map.gif" border="0" style="margin-top:2px"></a><br>
<strong>Contact:</strong> Jack Hatfield &nbsp;<br>
</p>
        """,
    )
    assert extract_center_info(*tags, page_number=1) == {
        "name": "Accidental Buddhist Sangha",
        "page": 1,
        "Address": "IL",
        "Tradition": "Mahayana, Zen Buddhist Master Thich Nhat Hahn",
        "Affiliation": "Community of Mindful Living/Order of Interbeing",
        "Phone": "(630) 375-0881",
        "E-mail": "jackhat1@aol.com",
        "Contact": "Jack Hatfield",
    }


def test_html_elements_in_only_part_of_the_value() -> None:
    # This removes the `Address`, which is tested elsewhere.
    tags = create_tags(
        "Alaska Buddhist Center - Rimay Tenzin Ling",
        """<p class="entryDetail">
<strong>Tradition:</strong> Vajrayana, Tibetan,Gelugpa<br>
<strong>Phone:</strong> (907) 374-3200<br> 
<strong>E-mail:</strong> <a href="mailto:alaskabuddhistcenter@gmail.com">alaskabuddhistcenter@gmail.com</a><br>
<strong>Website:</strong> <a href="http://www.alaskabuddhistcenter.org/">http://www.alaskabuddhistcenter.org/</a><br>
<strong>Find on:</strong> <a href="http://mapof.it/Physical: 4448 Pikes Landing Road (UUFF building)&#10;Fairbanks, Alaska&#10;&#10;Mailing: P.O. Box 60062&#10;&#10; Fairbanks 99706 Alaska" target="_blank"><img align="absmiddle" src="images/map.gif" border="0" style="margin-top:2px"></a><br>
<strong>Main Contact:</strong> nevillejacobs@gmail.com &nbsp;<i>(Phone: 907.456.4780)</i><br>
</p>""",
    )
    assert extract_center_info(*tags, page_number=1) == {
        "name": "Alaska Buddhist Center - Rimay Tenzin Ling",
        "page": 1,
        "Tradition": "Vajrayana, Tibetan,Gelugpa",
        "Phone": "(907) 374-3200",
        "E-mail": "alaskabuddhistcenter@gmail.com",
        "Website": "http://www.alaskabuddhistcenter.org/",
        "Main Contact": "nevillejacobs@gmail.com (Phone: 907.456.4780)",
    }


def test_value_in_key_strong_element() -> None:
    # Removes the address, already tested elsewhere with other centers.
    tags = create_tags(
        "American Young Buddhist Association",
        """<p class="entryDetail">
<strong>Tradition:</strong> Mahayana, Humanistic Buddhism<br>
<strong>Find on:</strong> <a href="http://mapof.it/3456 Glenmark Drive Hacienda Heights       91745 California" target="_blank"><img align="absmiddle" src="images/map.gif" border="0" style="margin-top:2px"></a><br>
<strong>Contact: Vice-secretary General:</strong> Ven. Hui-Chuang &nbsp;<br>
</p>""",
    )
    assert extract_center_info(*tags, page_number=1) == {
        "name": "American Young Buddhist Association",
        "page": 1,
        "Tradition": "Mahayana, Humanistic Buddhism",
        "Contact": "Vice-secretary General: Ven. Hui-Chuang",
    }


def test_two_entries_for_key() -> None:
    # This removes the Notes section, which is tested elsewhere.
    tags = create_tags(
        "Albuquerque Vipassana Sangha",
        """<p class="entryDetail">
<strong>Address:</strong>            &nbsp; Albuquerque NM 87196    <br>
<strong>Tradition:</strong> Theravada, Vipassana (Insight Meditation)<br>
<strong>Website:</strong> <a href="http://abqsangha.org">http://abqsangha.org</a><br>
<strong>Find on:</strong> <a href="http://mapof.it/            Albuquerque 87196     New Mexico" target="_blank"><img align="absmiddle" src="images/map.gif" border="0" style="margin-top:2px"></a><br>
<strong>Community Dharma Leader:</strong> Kathryn Turnipseed &nbsp;<br>
<strong>Community Dharma Leader:</strong> Valerie Roth &nbsp;<br>
        """,
    )
    assert extract_center_info(*tags, page_number=1) == {
        "name": "Albuquerque Vipassana Sangha",
        "page": 1,
        "Address": "Albuquerque NM 87196",
        "Tradition": "Theravada, Vipassana (Insight Meditation)",
        "Website": "http://abqsangha.org",
        "Community Dharma Leader": "Kathryn Turnipseed, Valerie Roth",
    }


def test_a_element_uses_href() -> None:
    tags = create_tags(
        "Amitabha Foundation",
        """<p class="entryDetail">
<strong>Address:</strong> 109 Irvington Road &nbsp; Rochester NY 14620<br>
<strong>Tradition:</strong> Vajrayana, Tibetan, Drikung Kagyu<br>
<strong>Affiliation:</strong> Ayang Rinpoche<br>
<strong>Phone:</strong> 585-261-7094<br> 
<strong>E-mail:</strong> <a href="mailto:ny@amitabhafoundation.us">ny@amitabhafoundation.us</a><br>
<strong>Website:</strong> <a href="http://www.amitabhafoundation.us">http://www.amitabhafoundation.us</a><br>
<strong>Find on:</strong> <a href="http://mapof.it/109 Irvington Road  Rochester 14620 New York" target="_blank"><img align="absmiddle" src="images/map.gif" border="0" style="margin-top:2px"></a><br>
<strong>Main Contact:</strong> Becky &nbsp;<a href="mailto:ny@amitabhafoundation.us">Email</a> &nbsp;<i>(Phone: 585-261-7094)</i><br>
</p>""",
    )
    assert extract_center_info(*tags, page_number=1) == {
        "name": "Amitabha Foundation",
        "page": 1,
        "Address": "109 Irvington Road, Rochester NY 14620",
        "Tradition": "Vajrayana, Tibetan, Drikung Kagyu",
        "Affiliation": "Ayang Rinpoche",
        "Phone": "585-261-7094",
        "E-mail": "ny@amitabhafoundation.us",
        "Website": "http://www.amitabhafoundation.us",
        "Main Contact": "Becky ny@amitabhafoundation.us (Phone: 585-261-7094)",
    }


def test_space_in_key_name() -> None:
    tags = create_tags(
        "Aung Mangalar Buddhist Temple",
        """<p class="entryDetail">
<strong>Tradition:</strong> Theravada, Burmese<br>
<strong>Venerable :</strong> Nagasena<br>
</p>""",
    )
    assert extract_center_info(*tags, page_number=1) == {
        "name": "Aung Mangalar Buddhist Temple",
        "page": 1,
        "Tradition": "Theravada, Burmese",
        "Venerable": "Nagasena",
    }


def test_notes_section() -> None:
    # This removes the Community Dharma Leader duplicate keys, which is tested elsewhere.
    tags = create_tags(
        "Albuquerque Vipassana Sangha",
        """<p class="entryDetail">
<strong>Address:</strong>            &nbsp; Albuquerque NM 87196    <br>
<strong>Tradition:</strong> Theravada, Vipassana (Insight Meditation)<br>
<strong>Website:</strong> <a href="http://abqsangha.org">http://abqsangha.org</a><br>
<strong>Find on:</strong> <a href="http://mapof.it/            Albuquerque 87196     New Mexico" target="_blank"><img align="absmiddle" src="images/map.gif" border="0" style="margin-top:2px"></a><br>
<strong>Notes and Events:</strong></p><p class="entryDesc">Contact :PO Box 40722 Albuquerque NM 87196<br></p>
        """,
    )
    assert extract_center_info(*tags, page_number=1) == {
        "name": "Albuquerque Vipassana Sangha",
        "page": 1,
        "Address": "Albuquerque NM 87196",
        "Tradition": "Theravada, Vipassana (Insight Meditation)",
        "Website": "http://abqsangha.org",
        "Notes and Events": "Contact :PO Box 40722 Albuquerque NM 87196",
    }

    tags = create_tags(
        "Dzogchen Community, Colorado",
        """<p class="entryDetail">
<strong>Tradition:</strong> Non-Sectarian, Dzogchen in the Transmission of Namkhai Norbu Rinpoche<br>
<strong>Notes and Events:</strong></p>
<p class="entryDesc"><!--StartFragment--></p>
<p>The Dzogchen Community of Colorado is a group of practitioners dedicated to practicing the transmission given to us by Namkhai Norbu Rinpoche. The Dzogchen, or “Great Perfection” are open to anyone who is interested, regardless of culture or religious tradition.</p>
<p>In the words of our teacher, “The Dzogchen teachings are neither a philosophy, nor a religious doctrine, nor a cultural tradition. Understanding the message of the teachings means discovering one’s own true condition stripped of all the self-deceptions and falsifications that the mind creates. The very meaning of the Tibetan term Dzogchen, ‘Great Perfection,’ refers to the true primordial state of every individual and not to any transcendent reality.” — from Dzogchen, The Self Perfected State by Namkhai Norbu.</p>
<!--EndFragment-->
<p></p>
<p></p>
<hr>
""",
    )
    assert extract_center_info(*tags, page_number=1) == {
        "name": "Dzogchen Community, Colorado",
        "page": 1,
        "Tradition": "Non-Sectarian, Dzogchen in the Transmission of Namkhai Norbu Rinpoche",
        "Notes and Events": (
            "The Dzogchen Community of Colorado is a group of practitioners dedicated to "
            "practicing the transmission given to us by Namkhai Norbu Rinpoche. The Dzogchen, "
            "or “Great Perfection” are open to anyone who is interested, regardless of culture or "
            "religious tradition.\n\n"
            "In the words of our teacher, “The Dzogchen teachings are neither a philosophy, nor a "
            "religious doctrine, nor a cultural tradition. Understanding the message of the "
            "teachings means discovering one’s own true condition stripped of all the "
            "self-deceptions and falsifications that the mind creates. The very meaning of the "
            "Tibetan term Dzogchen, ‘Great Perfection,’ refers to the true primordial state of "
            "every individual and not to any transcendent reality.” — from Dzogchen, The Self "
            "Perfected State by Namkhai Norbu."
        ),
    }


def test_address_remove_extra_state() -> None:
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
    assert extract_center_info(*tags, page_number=1) == {
        "name": "96th Street Sangha",
        "page": 1,
        "Address": "275 W. 96th Street, #4C New York, NY 10025",
        "Tradition": "Mahayana, Zen/Pureland",
        "Affiliation": "Higashi Honganji",
        "Phone": "(212) 749-1127",
        "E-mail": "gyobun@aol.com",
        "Main Contact": "T. Davis",
        "Spiritual Director": "Rev. Thulani Davis",
    }


def test_address_remove_whitespace_in_between_street_and_state() -> None:
    tags = create_tags(
        "Albuquerque Zen Center",
        """<p class="entryDetail">
<strong>Address:</strong> 2300 Garfield SE      &nbsp; Albuquerque NM 87106  <br>
<strong>Tradition:</strong> Mahayana, Rinzai Zen<br>
<strong>Phone:</strong> (505) 268-4877<br> 
<strong>E-mail:</strong> <a href="mailto:officeazc@gmail.com">officeazc@gmail.com</a><br>
<strong>Website:</strong> <a href="http://www.azc.org">http://www.azc.org</a><br>
<strong>Find on:</strong> <a href="http://mapof.it/2300 Garfield SE       Albuquerque 87106   New Mexico" target="_blank"><img align="absmiddle" src="images/map.gif" border="0" style="margin-top:2px"></a><br>
<strong>Contact:</strong> Seiju Mammoser &nbsp;<br>
</p>""",
    )
    assert extract_center_info(*tags, page_number=1) == {
        "name": "Albuquerque Zen Center",
        "page": 1,
        "Address": "2300 Garfield SE, Albuquerque NM 87106",
        "Tradition": "Mahayana, Rinzai Zen",
        "Phone": "(505) 268-4877",
        "E-mail": "officeazc@gmail.com",
        "Website": "http://www.azc.org",
        "Contact": "Seiju Mammoser",
    }

    # Contact removed because it's handled by another test.
    tags = create_tags(
        "American Young Buddhist Association",
        """<p class="entryDetail">
<strong>Address:</strong> 3456 Glenmark Drive&nbsp; Hacienda Heights       CA 91745<br>
<strong>Tradition:</strong> Mahayana, Humanistic Buddhism<br>
<strong>Find on:</strong> <a href="http://mapof.it/3456 Glenmark Drive Hacienda Heights       91745 California" target="_blank"><img align="absmiddle" src="images/map.gif" border="0" style="margin-top:2px"></a><br>
</p>""",
    )
    assert extract_center_info(*tags, page_number=1) == {
        "name": "American Young Buddhist Association",
        "page": 1,
        "Address": "3456 Glenmark Drive, Hacienda Heights CA 91745",
        "Tradition": "Mahayana, Humanistic Buddhism",
    }

    tags = create_tags(
        "All One Dharma-Quaker House   ",
        """<p class="entryDetail">
<strong>Address:</strong> 1440 Harvard Street,
         &nbsp; Santa Monica CA 90404<br>
</p>""",
    )
    assert extract_center_info(*tags, page_number=1) == {
        "name": "All One Dharma-Quaker House",
        "page": 1,
        "Address": "1440 Harvard Street, Santa Monica CA 90404",
    }


def test_address_remove_mailing_address() -> None:
    # This removes the `Main Contact`, which is tested elsewhere.
    tags = create_tags(
        "Alaska Buddhist Center - Rimay Tenzin Ling",
        """<p class="entryDetail">
<strong>Address:</strong> Physical: 4448 Pikes Landing Road (UUFF building)
Fairbanks, Alaska

Mailing: P.O. Box 60062

&nbsp; Fairbanks AK 99706<br>
<strong>Tradition:</strong> Vajrayana, Tibetan,Gelugpa<br>
<strong>Phone:</strong> (907) 374-3200<br> 
<strong>E-mail:</strong> <a href="mailto:alaskabuddhistcenter@gmail.com">alaskabuddhistcenter@gmail.com</a><br>
<strong>Website:</strong> <a href="http://www.alaskabuddhistcenter.org/">http://www.alaskabuddhistcenter.org/</a><br>
<strong>Find on:</strong> <a href="http://mapof.it/Physical: 4448 Pikes Landing Road (UUFF building)&#10;Fairbanks, Alaska&#10;&#10;Mailing: P.O. Box 60062&#10;&#10; Fairbanks 99706 Alaska" target="_blank"><img align="absmiddle" src="images/map.gif" border="0" style="margin-top:2px"></a><br>
</p>""",
    )
    assert extract_center_info(*tags, page_number=1) == {
        "name": "Alaska Buddhist Center - Rimay Tenzin Ling",
        "page": 1,
        "Address": "4448 Pikes Landing Road (UUFF building), Fairbanks, Alaska",
        "Tradition": "Vajrayana, Tibetan,Gelugpa",
        "Phone": "(907) 374-3200",
        "E-mail": "alaskabuddhistcenter@gmail.com",
        "Website": "http://www.alaskabuddhistcenter.org/",
    }
