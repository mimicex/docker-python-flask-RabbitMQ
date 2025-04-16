FROM python:3.8

WORKDIR /rabbit_python

RUN /usr/local/bin/python -m pip install --upgrade pip

COPY requirements.txt ./

RUN python -m pip install -r /rabbit_python/requirements.txt

COPY . /rabbit_python

CMD ["python", "main.py"]