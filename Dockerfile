FROM python:2.7-slim
ENV PYTHONUNBUFFERED 1
COPY hstore.sql /docker-entrypoint-initdb.d

RUN \
  apt-get -y update && \
  apt-get install -y gettext && \
  apt-get install -y python-dev && \
  apt-get install -y libpq-dev && \
  apt-get install -y gcc && \
  apt-get clean

ADD requirements.txt /app/
RUN pip install -r /app/requirements.txt

ADD . /app
WORKDIR /app

EXPOSE 8000
ENV PORT 8000

CMD ["uwsgi", "/app/saleor/wsgi/uwsgi.ini"]
