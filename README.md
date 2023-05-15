# Network Security Assignment 1
### For Computer Science B.Sc. Ariel University

**By Shahar Zaidel and Roy Simanovich**

## Description
In this assignment we simulated a diode in an enterprise network,
via 2 proxy servers. The assignment was built in Python. We used 4
docker machines to simulate the enterprise network. The assignment contains
4 main programs, each of which represents a computer in the network.
Our goal is to build a network in such a way that a user in an
enterprise network will be able to send data to the enterprise’s
super-duper secret server, without any data leaks from the server
itself. The network structure we built contains also two additional
proxy servers, one for each side, and a logical diode (to simulate a
real-life physical diode), that connects between the two proxy servers. 

The user and proxy 1 communicate via TCP protocol. The server and proxy
2 also communicate via TCP protocol. The proxy 1 server communicates
with proxy 2 server via a custom Reliable UDP protocol. Since the diode
is a logical diode, there isn’t actually a fifth component, and the
logical part of the diode is implemented in the programs of proxy 1
and proxy 2. We send the data in such way that the file that’s
transmitted is saved under the original MD5 hash name, and the end-user
(server) can compare between the name of the file and the MD5 hash of
the file and check if he received all the data without any interference.
We added a security layer by saving the received file by the name of the
MD5 hash of the file.


## Requirements

* Full linux (Ubuntu 22.04 LTS recommended)
* Python 3.10
* Docker-Compose (latest version)

We highly recommend using Dockers in order to run the program.
Using Dockers will allow you to run the program on few different machines on a single machine.

## Installation

1. First, install Docker-Compose:
You can find the installation instructions here: https://linuxhint.com/install-docker-compose-ubuntu-22-04/

2. Open a new Directory in your computer.
3. Paste the attached "docker-compose.yml" file in your new directory.
Note: Do not change the docker-compose.yml file contents unless you know what you are doing. 
4. Open a new subdirectory in your new directory named "volumes".
5. Paste the attached "proxy1.py", "proxy2.py", "enduser.py" and "sender.py" files in your new subdirectory - "volumes".
6. move the file that you want to send to the server through our data-diode to the "volumes" subdirectory.

## Running (Linux)
1. open 5 terminals and navigate to your new subdirectory.
2. In the first terminal, run the following command:
```
sudo docker-compose up
```
3. In the 4 other terminals, run the following command to enter each container's shell:
```
sudo docker exec -it <container-id> /bin/bash
```
then, enter the "volume" directory in each container:
```
cd volumes
```

4. In each container, run the following command to run the program:
```
python3 <program-name>.py
```
run the write command according to the container you are in:
for example, if you are in the enduser container, run the following command:
```
python3 enduser.py
```

If you want to see which containers are currently alive, run the following command:
```
sudo docker ps -a
```

In order to exit the docker, just type "exit" in the shell.
In order to stop all the dockers, press ctrl+c in the terminal you ran the "sudo docker-compose up" command.


## Running (Linux)
On your brand new dockers run the following commands: (the order is important, run each command in a different terminal)
```
python3 proxy1.py
python3 proxy2.py
python3 enduser.py
python3 sender.py
```
