# TFTP
Implementation of Trivial File Transfer Protocol in Python, versions based on RFC1350 and RFC7440

Docummentation:
https://tools.ietf.org/html/rfc1350
https://tools.ietf.org/html/rfc7440

How to use:

1350:
Client - python cl1350.py HOST name1 name2
where HOST - ipaddress of a server(probably localhost for testing),
name1 - name of file which we want to get,
name2 - name of file in which we will save data.

Server - python sv1350.py PORT x
where PORT - number of port on which we will listen(clients are defautly connecting to 6969),
x - path to the directory in which we are looking up for files.

7440:
Client - python cl1350.py HOST name1 name2 SIZE
where SIZE - expected windowsize
Server - python sv1350.py PORT x

Enjoy :)
