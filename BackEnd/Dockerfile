FROM python:latest

WORKDIR /workspace

COPY ./compress_api/* ./compress_api/
COPY ./setup.py .
COPY ./instance/* ./instance/

RUN pip install --upgrade pip
RUN pip install -e .

ENV FLASK_APP="compress_api"
ENV DB_HOST="172.31.13.57"
ENV DB_DB="compress_database"
ENV DB_USER="compress_user"
ENV DB_PORT="5432"
#ENV DB_PW="$$53eer3&777R"
#ENV FLASK_DEBUG=1

EXPOSE 5000

CMD ["flask", "run", "--host=0.0.0.0"]
