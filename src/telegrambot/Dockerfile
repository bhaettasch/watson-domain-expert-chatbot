# please replace APITOKEN and BACKENDBASEURL with the correct parameters
# to build: docker build -t telegrambot .
# to run: docker run --name telegrambot -d telegrambot

FROM python:3

ADD ./watsonbot.py /
ADD ./requirements.txt /

RUN pip install -r /requirements.txt

CMD [ "python3", "/watsonbot.py", "APITOKEN", "BACKENDBASEURL" ]
