FROM python:3.9.7-slim-buster

COPY . /python
WORKDIR /python


RUN pip install -r requirements.txt

ENTRYPOINT python jpws.py