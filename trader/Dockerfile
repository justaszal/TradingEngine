FROM python:3.5

ENV PROJECT_DIR=trader

RUN mkdir ${PROJECT_DIR}

WORKDIR ${PROJECT_DIR}

ADD . ./

RUN pip install -r requirements.txt
