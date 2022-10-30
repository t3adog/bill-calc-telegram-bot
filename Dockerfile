FROM python:3

RUN pip install python-telegram-bot --pre

ADD main.py /

CMD [ "python", "./main.py" ]