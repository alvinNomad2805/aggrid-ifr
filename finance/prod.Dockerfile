FROM python:3.9-slim

WORKDIR /finance

COPY ./requirements.txt /finance/requirements.txt

RUN pip install --upgrade pip

RUN pip install --no-cache-dir --upgrade -r /finance/requirements.txt

COPY . /finance

COPY dms.crt /etc/ssl/certs/dms.crt

COPY dms.key /etc/ssl/private/dms.key

EXPOSE 8020

CMD ["streamlit","run", "--server.port=8020","--server.sslCertFile=/etc/ssl/certs/dms.crt","--server.sslKeyFile=/etc/ssl/private/dms.key","--server.address=0.0.0.0","--server.enableCORS=false","--server.enableXsrfProtection=false","Finance.py"]