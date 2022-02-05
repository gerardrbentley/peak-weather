import asyncio

import pandas as pd
import streamlit as st
from structlog import get_logger

from helpers import (
    fromtimestamp,
    show_weather,
    WeatherItem,
    gather_one_call_weather_data,
    clean_time,
)

log = get_logger()
st.set_page_config(
    layout="wide",
    page_title="Peak Weather: 4,000 Footers",
    page_icon=":mountain:",
)


@st.cache()
def load_data(lat_lon_pairs: list) -> list:
    """Function to fetch Open Weather data and cache results

    Args:
        lat_lon_pairs (list): Destinations to get data for

    Returns:
        list: List of dictionaries which are json responses from open weather
    """
    log.info(f"Start Load Data")
    data = asyncio.run(gather_one_call_weather_data(lat_lon_pairs))
    log.info(f"Returning Load Data")
    return data


def main():
    """Main Streamlit App Entrypoint"""
    st.title(
        ":sunny::mountain::rainbow: Peak Weather of the 4,000 Footers :rainbow::mountain::sunny:"
    )
    st.header(":umbrella: You can't stop the rain, but you can spot it! :umbrella:")
    with st.expander("Expand for Basic App Information:"):
        st.markdown(
            """\
# Peak Weather: New Hampshire's 4,000 Footers

Built to give you a dashboard view of the next few hours' forecast for New Hampshires 48 4,000 ft mountains.
Gonna rain on the Kinsmans?
Is it snowing on Washington?
Should I hike Owl's Head?

Powered by [Streamlit](https://docs.streamlit.io/) + [Open Weather API](https://openweathermap.org/api).
Specifically, Streamlit runs the web interactinos and OpenWeather provides the data.

With :heart: from [Gar's Bar](https://tech.gerardbentley.com) by Gerard Bentley
"""
        )
    with st.spinner("Loading Mountain List"):
        base_mountains = pd.read_csv("./data/mountains.csv")

    with st.expander("Expand for Basic Mountain Information: "):
        st.dataframe(base_mountains)

    with st.spinner("Fetching Weather Data"):
        lat_lon_pairs = zip(base_mountains.lat, base_mountains.lon)
        weather_responses = load_data(lat_lon_pairs)

    first_response = weather_responses[0]
    st.write(
        f"## Time: {fromtimestamp(first_response['current']['dt']).strftime('%I:%M:%S %p, %b %d %Y')}"
    )

    for mountain, response in zip(base_mountains.name, weather_responses):
        st.write("-" * 88)
        st.write(f"#### {mountain}")
        col1, col2, col3, col4, col5 = st.columns(5)

        col1.write(f"Weather {clean_time(response['current']['dt'])}: ")
        current_temperature = round(response["current"]["temp"], 1)
        col1.metric("Temp (F)", current_temperature, 0.0)
        for weather in response["current"]["weather"]:
            weather_item = WeatherItem(**weather)
            show_weather(weather_item, col1)

        future_cols = [col2, col3, col4, col5]
        for col, entry in zip(future_cols, response["hourly"]):
            col.write(f"{clean_time(entry['dt'])}")
            temperature = round(entry["temp"], 1)
            col.metric(
                "Temp (F)", temperature, round(temperature - current_temperature, 1)
            )
            for weather in entry["weather"]:
                weather_item = WeatherItem(**weather)
                show_weather(weather_item, col)
            current_temperature = temperature
        alerts = response.get("alerts")
        if alerts is not None:
            with st.expander(f"View Weather Alerts for {mountain}"):
                for alert in alerts:
                    body = (
                        f"### Alert From {alert['sender_name']}: {alert['event']}",
                        f"Duration: {fromtimestamp(alert['start'])} - {fromtimestamp(alert['end'])}",
                        alert["description"],
                        f"Tags: {'; '.join(alert['tags'])}",
                    )

                    st.warning("\n".join(body))


if __name__ == "__main__":
    main()
