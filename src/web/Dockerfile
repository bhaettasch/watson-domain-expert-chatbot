FROM python:3.6

RUN apt-get update && apt-get install -y nginx supervisor npm nodejs-legacy
RUN pip install uwsgi
RUN npm install -g bower

RUN echo "daemon off;" >> /etc/nginx/nginx.conf
COPY nginx.conf /etc/nginx/sites-available/default

ADD . /srv
WORKDIR /srv

EXPOSE 80
CMD script/update --prod && supervisord
