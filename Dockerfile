FROM python:3.10.13-alpine3.18

ENV PYTHONUNBUFFERED=1

COPY ./requirements.txt /requirements.txt
RUN pip install --no-cache-dir --upgrade pip -r /requirements.txt

COPY ./src /opt/app
WORKDIR /opt/app

ENV DB_PATH=/opt/app/data/domains.db
VOLUME /opt/app/data

CMD sh -c "python main.py ${DB_PATH}"
