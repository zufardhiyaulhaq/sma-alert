FROM python:3

WORKDIR /home/sma-alert

copy . .

RUN pip install -r requirements.txt
CMD [ "python", "./sma.py" ]
