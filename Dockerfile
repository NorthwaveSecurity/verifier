# syntax=docker/dockerfile-upstream:master
FROM python:latest as base

RUN mkdir -p /root/.config && \
    mkdir /data

# Get SSH host key
RUN mkdir -p -m 0700 ~/.ssh && \
    ssh-keyscan github.com >> ~/.ssh/known_hosts

RUN apt update && \
    apt install -y --no-install-recommends nmap bsdmainutils dnsutils

COPY . /opt/verifier

WORKDIR /opt/verifier

RUN --mount=type=ssh pip install --no-cache-dir -e .[default]

# Configure verifier
ENV CONFIG_LOCATION /root/.config/verifier.ini
RUN test -f verifier.ini \
    && cp config.ini $CONFIG_LOCATION \
    || cp config.sample.ini $CONFIG_LOCATION

VOLUME /root/.config
VOLUME /data

ENV PYTHONUNBUFFERED 1

ENTRYPOINT ["verifier"]
