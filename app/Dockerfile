FROM python:3.8 AS builder
COPY ./* /var/www/shared/app/
WORKDIR /var/www/shared/app
RUN pip install virtualenv
RUN make venv
RUN . venv/bin/activate
RUN pip install -e .

EXPOSE 8080

RUN apt-get update -y && \
        DEBIAN_FRONTEND=noninteractive apt-get install -y \
        curl \
        libpq5 \
        libxml2 \
        && rm -r /var/lib/apt/lists/*

ENTRYPOINT ["/bin/sh"]
CMD ["/var/www/shared/app/scripts/run.sh"]

