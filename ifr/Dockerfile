FROM python:3.12-slim

WORKDIR /ifr-aggrid

COPY ./requirements.txt /ifr-aggrid/requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir --upgrade -r /ifr-aggrid/requirements.txt

COPY . /ifr-aggrid

EXPOSE 7050

CMD ["streamlit","run", "--server.port=7050","IFR.py"]