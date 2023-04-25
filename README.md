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
(server) can compere between the name of the file and the MD5 hash of
the file and check if he received all the data without any interference.
We added a security layer by saving the received file by the name of the
MD5 hash of the file.


## Requirements
* Linux (Ubuntu 22.04 LTS recommanded)/Windows machine
* Python 3

## Running (Windows)
```
python proxy1.py
python proxy2.py
python enduser.py
python sender.py
```

## Running (Linux)
```
python3 proxy1.py
python3 proxy2.py
python3 enduser.py
python3 sender.py
```
