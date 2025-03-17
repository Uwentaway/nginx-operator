FROM python:3.9.21-alpine3.21

RUN pip install kopf kubernetes

COPY ./operator.py /operator.py

CMD ["kopf", "run", "/operator.py"]

