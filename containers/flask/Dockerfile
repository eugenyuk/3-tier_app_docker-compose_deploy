FROM ubuntu:18.04

# Install bash within a container
#RUN apk --update add bash
RUN apt-get update && apt-get install -y \
	software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y \
	python3.7 \
	python3.7-dev \
	curl \
	python3-distutils \
	gcc && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.7 get-pip.py
#    apt-get install -y python3 python3-dev python3-pip uwsgi

# Create app's dir and make it current
RUN mkdir /flask

# Set current directory
WORKDIR /flask

# Set env variables
ENV FLASK_APP app.py
ENV FLASK_RUN_HOST 0.0.0.0

# Copy the file with requirements from host into
# container's current dir and install requirements
COPY ./requirements.txt .
RUN pip3 install -r ./requirements.txt

# Autostart uwsgi app server
CMD ["uwsgi", "--socket", "0.0.0.0:9000", "--wsgi-file", "app.py", "--callable", "app"]
