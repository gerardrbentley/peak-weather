# Peak Weather: New Hampshire's 4,000 Footers

Check it out [live on streamlit cloud](https://share.streamlit.io/gerardrbentley/peak-weather/main/streamlit_app/streamlit_app.py)

Built to give you a dashboard view of the next few hours' forecast for New Hampshires 48 4,000 ft mountains.
Gonna rain on the Kinsmans?
Is it snowing on Washington?
Should I hike Owl's Head?

Powered by [Streamlit](https://docs.streamlit.io/) + [Open Weather API](https://openweathermap.org/api).
Specifically, Streamlit runs the web interactinos and OpenWeather provides the data.

## Local Run

### Update OpenWeather connection secrets

Requires signing up for [Open Weather API Account](https://openweathermap.org/api).

Considered using [weather.gov feed](https://www.weather.gov/documentation/services-web-api), but found [Avra on YouTube](https://www.youtube.com/watch?v=Ky7mvS0m0nk) have success with Open Weather

- Copy or Rename `.env.example` as `.env.dev` and fill in the OPEN_WEATHER_API_KEY for your account (should come via email)

```sh
mv .env.example .env.dev
```

### Run with Docker

Requires [docker-compose](https://docs.docker.com/compose/install/) to be installed (this comes with Docker Desktop).

```sh
docker-compose up
# Open localhost:8501
```

Use `-d` to detach from logs.

Use `--build` on subsequent runs to rebuild dependencies / docker image.

### Lint, Check, Test with Docker

```sh
# Linting
docker-compose run streamlit-app nox.sh -s lint
# Unit Testing
docker-compose run streamlit-app nox.sh -s test
# Both
docker-compose run streamlit-app nox.sh
# As needed:
docker-compose build

# E2E Testing
docker-compose up -d --build
# Replace screenshots
docker-compose exec streamlit-app nox -s test -- -m e2e --visual-baseline
# Compare to visual baseline screenshots
docker-compose exec streamlit-app nox -s test -- -m e2e
# Turn off / tear down
docker-compose down
```

### Local Python environment

For code completion / linting / developing / etc.

```sh
python -m venv venv
. ./venv/bin/activate
# .\venv\Scripts\activate for Windows
python -m pip install -r ./streamlit_app/requirements.dev.txt
pre-commit install

# Linting / Static Checking / Unit Testing
python -m black streamlit_app
python -m isort --profile=black streamlit_app
python -m flake8 --config=./streamlit_app/.flake8 streamlit_app
```

## Features

- Containerization with [Docker](https://docs.docker.com/)
- Dependency installation with Pip
- Test automation with [Nox](https://nox.thea.codes/en/stable/index.html)
- Linting with [pre-commit](https://pre-commit.com/) and [Flake8](https://flake8.pycqa.org/en/latest/)
- Code formatting with [Black](https://black.readthedocs.io/en/stable/)
- Testing with [pytest](https://docs.pytest.org/en/6.2.x/getting-started.html)
- Code coverage with [Coverage.py](https://coverage.readthedocs.io/en/6.2/)


## Project Breakdown

Utilizes Open Weather API Endpoints:

### "One-Call" API

[Documentation](https://openweathermap.org/api/one-call-api)



