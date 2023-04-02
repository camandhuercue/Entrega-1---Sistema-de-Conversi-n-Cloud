FROM python:latest

WORKDIR /workspace

COPY ./queue_api/* ./queue_api/
COPY ./*.py .
copy ./init.sh /workspace

RUN chmod +x /workspace/init.sh

RUN mkdir -p /workspace/files
RUN mkdir -p /workspace/archive

RUN apt-get update

RUN pip install --upgrade pip
RUN pip install -e .

CMD [ "/workspace/init.sh" ]
