FROM python:3.8-slim

ARG VERSION

RUN pip3 install --upgrade pip && \
    # Workaround to fix vulnerability CVE-2022-40897 in base image
    pip3 install --upgrade setuptools && \
    pip3 install mtr2mqtt==$VERSION

# Workaround to fix vulnerability CVE-2023-47038 in base image
RUN apt-get update && apt-get upgrade -y perl-base

#RUN addgroup -g 50 serial && adduser -D -G serial -H mtr2mqtt
#USER mtr2mqtt
ENTRYPOINT mtr2mqtt