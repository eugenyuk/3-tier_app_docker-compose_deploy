# Hello world web app
This is a containerized hello world web application.

## Used technologies
* Nginx
* Python (Flask)
* uWSGI
* Docker (docker-compose)

## Nginx configuration & containerization
Dockerfile:
```
# Base image. To make sure it is always fresh, not set a version tag.
FROM	nginx
# Copy config file from host to the container
COPY	./site.conf /etc/nginx/conf.d/
```

site.conf:
```nginx
server {
    # Process requrests with header Host: 10.0.0.2
    server_name 10.0.0.2 flask-app.local;

    # Pass all requests to uWSGI app server
    location = / {
        uwsgi_pass flask:9000;
        include uwsgi_params;
    }
}
```

## Flask configuration & containerization
Dockerfile:
```
# Base image
FROM ubuntu:18.04

# Install required packages
RUN apt-get update && apt-get install -y \
	software-properties-common
RUN add-apt-repository ppa:deadsnakes/ppa
RUN apt-get update && apt-get install -y \
	python3.7 \
	python3.7-dev \
	curl \
	python3-distutils \
	gcc && \
    # This is a hack-install pip3.7 for ubuntu 18.04
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python3.7 get-pip.py

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
```

As it can be seen, uWSGI app server is configured to listen to socker 0.0.0.0:9000 and run *app* variable from file app.py for every new request.

## Docker-compose configuration

```
# Specify version 2 (not 3) because ansible doesn't
# support version 3 so far
version: '2.4'

services:
  nginx:
    build:
      # Build an image using a Dockerfile from this dir. 
      context: ./containers/nginx/
    ports:
      # Redirect requests host:80->container:80
      - 80:80
    networks:
      # Connect our container to the custom network
      flask-app-net:
        # Assign ip address
        ipv4_address: 10.0.0.2
  flask:
    build:
      context: ./containers/flask/
    volumes:
      - ./containers/flask:/flask
    ports:
      # Expose port 9000 to inside containers' LAN
      - 9000
    networks:
      flask-app-net:
        ipv4_address: 10.0.0.3

# Custom network description
networks:
  flask-app-net:
    ipam:
      config:
        - subnet: 10.0.0.0/16
          gateway: 10.0.0.1
```
Every service is described. Also, a custom network 10.0.0.0/16 with default gateway 10.0.0.1 is configured. Every service is connected to that network and static ip addresses are assigned.
