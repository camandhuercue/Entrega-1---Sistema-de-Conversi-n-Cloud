FROM python:latest

RUN apt-get update
RUN apt-get install redis-server -y

EXPOSE 6379

CMD ["redis-server", "--daemonize", "yes"]