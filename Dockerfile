FROM python:3.8-slim

ARG VERSION

RUN pip3 install mtr2mqtt==$VERSION

ENTRYPOINT mtr2mqtt