import requests
import requests_cache
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter

session = requests_cache.CachedSession()
adapter = HTTPAdapter(max_retries=5)
session.mount("https://", adapter)
session.mount("http://", adapter)


def load_person_from_worldcat(worldcat_url):
    try:
        r = session.get(worldcat_url)
        r.raise_for_status()
        bs = BeautifulSoup(r.content, features="lxml")
        title = bs.find("title")
        if title:
            title = title.text
            return {
                "title": title,
                "contributor": "https://www.worldcat.org/",
                "source": worldcat_url,
                "format_": "text/html"
            }
        return {}
    except requests.exceptions.HTTPError:
        return {}
