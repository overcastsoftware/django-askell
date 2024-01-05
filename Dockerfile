# Use an official Python runtime as a parent image
FROM python:3.12-bullseye
LABEL maintainer="hallo@overcast.is"

# Set environment varibles
ENV PYTHONUNBUFFERED 1

# Install libenchant and create the requirements folder.
RUN apt-get update -y \
    && apt-get install -y libenchant-2-dev postgresql-client \
    && mkdir -p /code/requirements

# Install the test_project project's dependencies into the image.
COPY ./test_project/requirements.txt /code/requirements.txt
RUN --mount=type=cache,target=/root/.cache/pip pip install --upgrade pip \
    && pip install -r /code/requirements.txt

# Install django-askell from the host. This folder will be overwritten by a volume mount during run time (so that code
# changes show up immediately), but it also needs to be copied into the image now so that django-askell can be pip install'd.
RUN mkdir /code/askell
COPY ./askell /code/askell/askell
COPY ./setup.py /code/askell/
COPY ./README.md /code/askell/

RUN cd /code/askell/ \
    && pip install -e .