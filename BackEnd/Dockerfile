FROM python:latest

WORKDIR /workspace

COPY ./compress_api .

RUN pip install --upgrade pip
RUN pip install -e .

ENV FLASK_APP="compress_api"
#ENV FLASK_DEBUG=1

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
