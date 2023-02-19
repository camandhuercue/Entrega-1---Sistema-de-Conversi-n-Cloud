FROM python:latest

WORKDIR /workspace

COPY ./queue_api/* ./queue_api/
COPY ./*.py .

RUN mkdir -p /workspace/files
RUN mkdir -p /workspace/archive

RUN apt-get update
RUN apt-get install redis-server -y
RUN redis-server --daemonize yes

RUN pip install --upgrade pip
RUN pip install -e .

CMD ["redis-server"]