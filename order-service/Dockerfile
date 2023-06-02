FROM python:3.11-slim

ENV RABBITMQ_HOST=${RABBITMQ_HOST}

RUN echo $RABBITMQ_HOST

WORKDIR /home/service

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["python", "consumer.py"]
