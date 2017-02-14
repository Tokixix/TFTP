#!/usr/bin/env python
from struct import *
import socket
import hashlib
import sys

#Preparing for connection:
PORT = 6969
HOST = sys.argv[1] 
Filename = sys.argv[2] 
My_filename = sys.argv[3]
Order = 1 
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.1)
Read = pack('!H', 1) 
Ack = pack('!H', 4)
Mode = "octet"
b = pack('!B', 0)
Message = Read + Filename + b + Mode + b

#Initial Pakcet:
while 1:
	try:
		Get, Adr = sock.recvfrom(1024) # This Adr will be the one which we will use in whole connection
		break 
	except socket.timeout: 
		sock.sendto(Message, (HOST, PORT)) 

#Error info check:
Opcode_rec = unpack('!H', Get[:2])
if Opcode_rec[0] == 5:
	print("File not found.")
	exit()
	
#Creating file for writing:
fil = open(My_filename, 'w+')
m = hashlib.md5()

#Connection Loop:
while 1:
	Block = unpack('!H', Get[2:4])
	Data = Get[4:]
	
	if Block[0] == Order: #Got new packet
		fil.write(Data)
		m.update(Data)
		Order += 1 #Lets wait for next packet
		Message = Ack + pack('!H', (Order - 1) % 65536) 
		sock.sendto(Message, Adr)
		
	#an else situation means that we got older packet, which had been ack so we can pass it
	if(len(Get) < 516): #waiting to be quite sure that server ended his work
		while 1:
			try:
				Get, adr = sock.recvfrom(1024)
				if adr != Adr:
					continue
				sock.sendto(Message, Adr) 
			except socket.timeout:
				break
		break
		
	while 1:
		try:
			Get, adr = sock.recvfrom(1024) 
			if adr != Adr:
				continue
			break
		except socket.timeout:
			sock.sendto(Message, Adr)

#Printing md5:
print(m.hexdigest())
