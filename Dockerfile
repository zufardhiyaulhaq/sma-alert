FROM python:3

WORKDIR /home/sma-alert

ADD requirements.txt .
ADD sma.py .

RUN pip install -r requirements.txt
CMD [ "python", "./sma.py" ]