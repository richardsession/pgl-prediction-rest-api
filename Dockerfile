FROM ubuntu:18.04

RUN apt-get update && apt-get install -y python3 python3-pip python3-venv python3-setuptools cmake libmagic-dev build-essential libssl-dev libffi-dev 
RUN pip3 install --upgrade pip

RUN mkdir -p /var/www/greenlight-rest-api
WORKDIR /var/www/greenlight-rest-api
COPY . .
RUN chmod +w /var/www/greenlight-rest-api/uploads
RUN mv .env.example .env

ENV PIP_DEFAULT_TIMEOUT=100
RUN pip3 install -r requirements.txt

EXPOSE 8000

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app"]