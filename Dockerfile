FROM python:3.12-slim-bookworm

WORKDIR /webServer

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . /webServer/

CMD [ "python3", "main.py" ]