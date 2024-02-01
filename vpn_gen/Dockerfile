FROM ubuntu:20.04

RUN apt-get update && \
    apt-get install -y openvpn

COPY result/server/jury/* ./
COPY result/server/team/* ./
COPY result/server/vuln/* ./


CMD for conf in $(ls *.conf); do \
        openvpn --config "$conf" --daemon; \
    done && \
    tail -f /dev/null
