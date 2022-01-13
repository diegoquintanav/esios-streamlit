# base image
FROM continuumio/miniconda3

# set working directory
WORKDIR /app

# add and install requirements
COPY environment.yml /app/environment.yml

# create environment
RUN conda update conda
RUN conda env create -f /app/environment.yml

# add app
COPY . /app

# run server
CMD ["conda", "run", "-n", "esios-app", "streamlit", "run", "app.py"]