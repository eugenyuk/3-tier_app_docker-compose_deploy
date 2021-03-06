# Hello world web app
This is a containerized hello world 3-tier web application.

## Used technologies
* Nginx
* Python3.7 (Flask)
* uWSGI
* Docker (docker-compose)
* Postgres 9.3

## Nginx configuration & containerization
Dockerfile:
```dockerfile
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
To comply with the requirement to use Ubuntu 18.04, the app is built using ubuntu:18.04 image.

Dockerfile:
```dockerfile
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
To 
As it can be seen, uWSGI app server is configured to listen to socker 0.0.0.0:9000 and run *app* variable from file app.py for every new request.

## Docker-compose configuration

```dockerfile
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
  postgres:
    # Take the image
    image: postgres:9.3
    # Redirect connection host:5432->container:5432
    ports:
      - "5432:5432"
    environment:
      # To create user
      - POSTGRES_USER=test
      # To make a password for external connections
      - POSTGRES_PASSWORD=test
      # To create a db
      - POSTGRES_DB=test_db
    volumes:
      # Mount host dir into container to store data persistently
      - ./containers/postgres/data:/var/lib/postgresql/data
    networks:
      flask-app-net:
        ipv4_address: 10.0.0.4

# Custom network description
networks:
  flask-app-net:
    ipam:
      config:
        - subnet: 10.0.0.0/16
          gateway: 10.0.0.1
```
Every service is described. Also, the custom network 10.0.0.0/16 with default gateway 10.0.0.1 is configured. Every service is connected to that network and static ip addresses are assigned.

## How to deploy

Run using docker-compose:
```bash
[ansible-deploy]$ docker-compose up -d
Starting ansible-deploy_flask_1    ... done
Starting ansible-deploy_nginx_1    ... done
Starting ansible-deploy_postgres_1 ... done
```

Check if containers are up:
```bash
[ansible-deploy]$ docker-compose ps
          Name                         Command               State            Ports         
--------------------------------------------------------------------------------------------
ansible-deploy_flask_1      uwsgi --socket 0.0.0.0:900 ...   Up      0.0.0.0:32786->9000/tcp
ansible-deploy_nginx_1      nginx -g daemon off;             Up      0.0.0.0:80->80/tcp     
ansible-deploy_postgres_1   docker-entrypoint.sh postgres    Up      0.0.0.0:5432->5432/tcp
```

In browser, go to http://10.0.0.2/
