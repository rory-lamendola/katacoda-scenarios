FROM python:3.8 AS builder
COPY ./* /var/www/shared/interviews
WORKDIR /var/www/shared/interviews
RUN pip install virtualenv
RUN make venv

EXPOSE 8080

RUN apt-get update -y && \
        DEBIAN_FRONTEND=noninteractive apt-get install -y \
        curl \
        libpq5 \
        libxml2 \
        && rm -r /var/lib/apt/lists/*

ENTRYPOINT ["/bin/sh"]
CMD ["/var/www/shared/interviews/scripts/run.sh"]

