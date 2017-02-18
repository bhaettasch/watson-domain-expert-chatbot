FROM python:3.6

RUN apt-get update && apt-get install -y npm nodejs-legacy
RUN npm install -g bower

ADD . /srv
WORKDIR /srv

RUN script/update

EXPOSE 80
CMD ./manage.py runserver 0.0.0.0:80
