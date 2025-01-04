FROM python:3.12-slim-bookworm

WORKDIR /webServer

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .

EXPOSE 8080

CMD [ "python3", "-m", "scripts.launch" ]