FROM python:3.12-slim

WORKDIR /finance

COPY ./requirements.txt /finance/requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir --upgrade -r /finance/requirements.txt

COPY . /finance

EXPOSE 7090

CMD ["streamlit","run", "--server.port=7090","--server.address=0.0.0.0","--server.enableCORS=false","--server.enableXsrfProtection=false","Finance.py"]
