FROM python:3.8-slim-buster

WORKDIR /home/sma-alert

COPY requirements.txt .
RUN pip install -r requirements.txt

copy . .

CMD [ "python", "./sma.py" ]
