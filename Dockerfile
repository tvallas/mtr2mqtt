FROM python:3.8-slim

ARG VERSION

RUN pip3 install --upgrade pip && \
    pip3 install --upgrade setuptools && \
    pip3 install mtr2mqtt==$VERSION

RUN addgroup -g 50 serial && adduser -D -G serial -H mtr2mqtt
USER mtr2mqtt
ENTRYPOINT mtr2mqtt