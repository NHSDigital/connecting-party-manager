FROM python:3.8-slim

ADD requirements.txt /requirements.txt
RUN pip install -r /requirements.txt

ADD entrypoint.py /entrypoint.py
ENTRYPOINT ["python", "/entrypoint.py"]
