FROM python:3.6
RUN touch /tmp/access.log
WORKDIR /usr/src
COPY . /usr/src
VOLUME [ "/tmp" ]
RUN pip3 install --editable .
