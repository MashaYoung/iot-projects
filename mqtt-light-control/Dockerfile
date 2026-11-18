FROM python:3.12-slim

WORKDIR /app

COPY  mqtt_light_node.py.py /app
RUN pip install paho-mqtt python-dotenv

CMD [ "python","mqtt_light_node.py.py"]

