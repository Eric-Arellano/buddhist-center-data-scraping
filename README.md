# US Buddhist Center data scraping

Scrape data from http://www.buddhanet.info/wbd/country.php?country_id=2.

Scraping code adapted from ChatGPT4, with this prompt:

```
Write a Python program that web scrapes http://www.buddhanet.info/wbd/country.php?country_id=2 and returns the result as JSON, with one entry per Buddhist center. 

Each entry has HTML like this:

<p class="entryName">96th Street Sangha</p>
<p class="entryDetail">
<strong>Address:</strong> 275 W. 96th Street, #4C New York, NY 10025                   &nbsp;  NY <br>
...
</p>
<hr>

The text inside the `<p class="entryName">` is the name of the Buddhist center.

Inside the `<p class="entryDetail">`, every `<strong>` is a new key name. The text or the <a> following that `<strong>` is the value for that key; if it's an <a>, I want to extract the text. The `<br>` separates each of those details.

Finally, the `<hr>` separates each Buddhist center entry.
```

## To run

First, install Pants: https://www.pantsbuild.org/docs/installation

* Scrape: `pants run scrape.py`
* Tests: `pants test :`
* Formatters: `pants fix :`
