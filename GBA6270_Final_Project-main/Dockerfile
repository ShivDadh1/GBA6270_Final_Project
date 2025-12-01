FROM python:3.10-slim

WORKDIR /opt/app
COPY . /opt/app

RUN pip install --upgrade pip \
 && pip install -r requirements.txt

ENV POLL_INTERVAL=5

CMD ["python", "bot_code.py"]
