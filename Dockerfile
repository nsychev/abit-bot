FROM python:alpine

WORKDIR /bot/
COPY bot/requirements.txt /bot/requirements.txt
RUN pip --no-cache-dir install -r requirements.txt
ENV PYTHONPATH=/bot/

COPY bot /bot/

