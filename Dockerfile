from python:alpine

WORKDIR /app
COPY requirements.txt .
RUN apk add --no-cache libffi-dev openssl-dev build-base && \
    pip install -r requirements.txt

COPY main.py .

ENTRYPOINT ["/app/main.py"]