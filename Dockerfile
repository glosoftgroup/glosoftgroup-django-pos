#FROM python:3.5

FROM buildpack-deps:jessie

ENV PYTHONUNBUFFERED 1

# ensure local python is preferred over distribution python
#ENV PATH /usr/local/bin:$PATH
#
#ENV LANG C.UTF-8

RUN \
  apt-get -y update && \
  apt-get install -y gettext && \
  apt-get -y install python-software-properties && \
  apt-get update && \
  apt-get -y install python-pip python-dev build-essential && \
  pip install --upgrade pip && \
  apt-get update && \
  apt-get -y install ansible && \
  apt-get clean

ADD requirements.txt /app/
RUN pip install -r /app/requirements.txt

ADD . /app
WORKDIR /app

EXPOSE 8000
ENV PORT 8000

CMD ["uwsgi", "/app/saleor/wsgi/uwsgi.ini"]
