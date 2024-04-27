FROM python:3.11-slim
WORKDIR /app
COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY . /app
CMD ["uvicorn", "api.endpoints:app", "--host", "0.0.0.0", "--port", "8080"]
