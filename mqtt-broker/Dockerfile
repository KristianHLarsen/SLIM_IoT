# Dockerfile References: https://docs.docker.com/engine/reference/builder/

# Start from python:3.8-alpine base image
FROM eclipse-mosquitto:1.6.12


# Make dir app
WORKDIR /etc/mosquitto/

COPY /mosquitto .


# Expose port 1883 to the outside world
EXPOSE 1883
