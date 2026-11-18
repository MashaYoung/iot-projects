FROM python:3.12-slim
WORKDIR /app
COPY climate_monitor.py /app
ENV BUTTON_ENABLED=0
CMD ["python", "-u", "climate_monitor.py"]
