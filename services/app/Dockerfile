# base image
FROM continuumio/miniconda3

# set working directory
WORKDIR /app

# add and install requirements
COPY environment.yml /app/environment.yml

# create environment
RUN conda update conda
RUN conda env create -f /app/environment.yml

# environment variables
ARG ESIOS_TOKEN

# env is available at runtime, which is useful only for debugging. It can be removed.
ENV ESIOS_TOKEN $ESIOS_TOKEN

# add app
COPY . /app

# download data and store it in /data folder
RUN ["conda", "run", "-n", "esios-app", "python", "request.py"]

# run server
CMD ["conda", "run", "-n", "esios-app", "streamlit", "run", "app.py"]