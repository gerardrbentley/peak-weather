import streamlit as st
from pydantic import BaseSettings, BaseModel
from datetime import datetime
import httpx
import pytz
import asyncio
from structlog import get_logger
log = get_logger()


class WeatherItem(BaseModel):
    id: int
    main: str
    description: str
    icon: str


class Settings(BaseSettings):
    """Handles fetching configuration from environment variables and secrets.
    Type-hinting for config as a bonus"""

    open_weather_api_key: str


settings = Settings()


class WeatherUnit:
    STANDARD = "standard"
    KELVIN = "standard"
    METRIC = "metric"
    IMPERIAL = "imperial"


def get_one_call_endpoint(
    lat: float,
    lon: float,
    units: WeatherUnit = WeatherUnit.IMPERIAL,
    exclude="",
    lang="en",
):
    if exclude != "":
        exclude = f"&exclude={exclude}"
    return f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={lon}&units={units}{exclude}&lang={lang}&appid={settings.open_weather_api_key}"


def get_icon_url(icon: str):
    return f"![Alt Text](http://openweathermap.org/img/wn/{icon}@2x.png)"


def show_weather(weather: WeatherItem, col=None):
    value = f"**Status**: {weather.main} ({weather.description})\n" + get_icon_url(
        weather.icon
    )
    if col is not None:
        col.markdown(value)
    else:
        st.markdown(value)


def fromtimestamp(timestamp: int) -> datetime:
    return datetime.fromtimestamp(timestamp, pytz.timezone("America/New_York"))


def clean_time(timestamp: int) -> str:
    return fromtimestamp(timestamp).strftime("%I:%M:%S %p")


async def get_one_call_data(client: httpx.AsyncClient, lat: float, lon: float) -> dict:
    """Given http client and valid lat lon, retrieves open weather "One call" API data

    Args:
        client (httpx.AsyncClient): To make requests. See httpx docs
        lat (float): lat of the desired location
        lon (float): lon of the desired location

    Returns:
        dict: json response from Open Weather One Call
    """
    endpoint = get_one_call_endpoint(lat, lon)
    response = await client.get(endpoint)
    return response.json()


async def gather_one_call_weather_data(lat_lon_pairs: list) -> list:
    """Given list of tuples of lat, lon pairs, will asynchronously fetch the one call open weather api data for those pairs

    Args:
        lat_lon_pairs (list): Destinations to get data for

    Returns:
        list: List of dictionaries which are json responses from open weather
    """
    async with httpx.AsyncClient() as client:
        tasks = [
            asyncio.ensure_future(get_one_call_data(client, lat, lon))
            for lat, lon in lat_lon_pairs
        ]
        one_call_weather_data = await asyncio.gather(*tasks)
        return one_call_weather_data
