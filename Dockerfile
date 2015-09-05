FROM python:3.4.3

WORKDIR /home

ADD . /home

RUN pip3 install -r requirements.txt

ENTRYPOINT ["python3", "main.py"]
