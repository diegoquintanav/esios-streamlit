# About

Code and notebooks for the a small streamlit app that requests demand data from the ESIOS REST API and displays it in time and frequency domain.

## Deploy streamlit app using docker-compose

1. Create an `.env` file and add your token as an environment variable named `ESIOS_TOKEN`. Check `.env.example` for an example.
2. With docker-compose, run `docker-compose up -d`
3. Go to <http://0.0.0.0:8501/>
4. You should be able to interact with the app

![example-app](./resources/app-example.png)
![example-time](./resources/time.png)
![example-freq](./resources/freq.png)

## Navigating source code

The application is located in the path `services/app/` and consists of two parts:

- a `request.py` script that performs the request and persists results on disk
- a `app.py` that consumes the data and launches the streamlit app on port `8501`

## Launching app without docker-compose

- go to the `services/app/` directory, and create a conda environment from the `environment.yml` file with `conda env create -f environment.yml`
- activate the environment with `conda activate esios-app`
- run `python request.py` to download the data
- run `streamlit run app.py` to launch the app
