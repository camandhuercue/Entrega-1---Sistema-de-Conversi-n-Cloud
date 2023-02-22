FROM python:latest

WORKDIR /workspace

COPY ./queue_api/* ./queue_api/
COPY ./*.py .

RUN mkdir -p /workspace/files
RUN mkdir -p /workspace/archive

RUN apt-get update

RUN pip install --upgrade pip
RUN pip install -e .

CMD ["celery", "-A", "tasks", "worker", "-l", "info"]