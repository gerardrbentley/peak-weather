import pandas as pd
import httpx
import asyncio
from bs4 import BeautifulSoup

# English Wikipedia
BASE_URL = "https://en.wikipedia.org"


def main():
    # Chunk from 4,000 footers page containing list of mountains
    # https://en.wikipedia.org/wiki/Four-thousand_footers
    soup = BeautifulSoup(open("wiki.html"), "html.parser")

    # Gather <a> tags, ignore citation
    links = [x for x in soup.find_all("a") if x.get("title")]
    # Async get all lat lon as list of dictionaries
    coords = asyncio.run(gather_coords(links))

    # Save dictionaries with pandas
    df = pd.DataFrame(coords)
    df.to_csv("coords.csv", index=False)

def convert(raw_tude: str) -> float:
    """Takes a wikipedia latitude or longitude string and converts it to float

    Args:
        raw_tude (str): Lat or Lon in one of the following forms:
            degrees°minutes′seconds″N,
            degrees°minutes′N,
            degrees-minutes-secondsN,
            degrees-minutesN

    Returns:
        (float): Float converted lat or lon based on supplied DMS
    """
    tude = raw_tude.replace("°", "-").replace("′", "-").replace("″", "")
    if tude[-2] == "-":
        tude = tude[:-2] + tude[-1]
    multiplier = 1 if tude[-1] in ["N", "E"] else -1
    return multiplier * sum(
        float(x) / 60 ** n for n, x in enumerate(tude[:-1].split("-"))
    )


async def get_coords(client: httpx.AsyncClient, a_link: BeautifulSoup) -> dict:
    """Given http client and <a> link from wikipedia list,
    Fetches the place's html page,
    Attempts to parse and convert lat and lon to decimal from the page (first occurrence)
    Returns entry with keys: "name", "link", "lat", "lon"

    Args:
        client (httpx.AsyncClient): To make requests. See httpx docs
        a_link (BeautifulSoup): <a> ... </a> chunk

    Returns:
        dict: coordinate entry for this wikipedia place
    """    
    name = a_link.get("title")
    link = a_link.get("href")
    raw_page = await client.get(BASE_URL + link)
    raw_soup = BeautifulSoup(raw_page, "html.parser")
    try:
        raw_lat = raw_soup.find(class_="latitude").text.strip()
        lat = convert(raw_lat)
    except Exception as e:
        print(e)
        lat = 0.0
    try:
        raw_lon = raw_soup.find(class_="longitude").text.strip()
        lon = convert(raw_lon)
    except Exception as e:
        print(e)
        lon = 0.0
    return {"name": name, "link": link, "lat": lat, "lon": lon}


async def gather_coords(links: list) -> list:

    async with httpx.AsyncClient() as client:
        tasks = [asyncio.ensure_future(get_coords(client, link)) for link in links]
        coords = await asyncio.gather(*tasks)
        return coords


if __name__ == "__main__":
    main()