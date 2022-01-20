To start and run the mqtt broker we use a ubuntu container: 

    docker run -it --name ubuntu-mqtt -p 1883:1883 ubuntu:18.4 
    docker run -it --name ubuntu-client2 ./ubuntu-client.tar


Further more the following commands are to be run inside the container: 

    apt-get update
    apt-get upgrade

    apt-get install mosquitto
    apt-get install mosquitto-clients

    apt-get install nano

    nano /etc/mosquitto/mosquitto.conf

paste the following into the open mosquitto.conf:

    allow_anonymous false
    password_file /etc/mosquitto/pwfile
    listener 1883

Then setup password and username. When running the command make sure to use `mqtt` as username and `123456` as password when prompted. 

mosquitto_passwd -c /etc/mosquitto/pwfile mqtt

In order to connect a client to the mqtt server the following line has to be added. for documentation go to 
http://www.steves-internet-guide.com/client-connections-python-mqtt/

    client.username_pw_set(username="mqtt",password="123456"

pwfile:

    mqtt:$6$4eCQ9mP53ENkrR5W$F7YeMTqaoaSDWdSR7QNh8QjxNbQ+3LA4Kq3O5eZJ7LXPL4CAaxBmmhYCgDCDjo2xyeTmsYwJZbaxKM1sYMhRJQ==



In order to test the service do the following: 

    docker network ls

inspect bridge to discover the ip of the broker. 

    docker network inspect bridge

documentation for networking in docker: 
https://docs.docker.com/config/containers/container-networking/



 check which services are running: 
 service --status-all

 mosquitto_sub -h 172.17.0.2 -d -u mqtt -P 123456 -t "dev/test"
 172.17.0.2
mosquitto_pub -h 172.17.0.2 -d -u mqtt -P 123456 -t "dev/test" -m "Hello world"



