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
SIZE = sys.argv[4]
Order = 0
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(0.1)
Read = pack('!H', 1)
Ack = pack('!H', 4)
Mode = "octet"
b = pack('!B', 0)
Message_1 = Read + Filename + b + Mode + b + "windowsize" + b + SIZE + b

#Initial Pakcet:
while 1:
	try:
		Answer, Adr = sock.recvfrom(1024) # This Adr will be the one which we use in the whole connection
		break 
	except socket.timeout: 
		sock.sendto(Message_1, (HOST, PORT))

#Error info check:
Opcode_rec = unpack('!H', Answer[:2])
if Opcode_rec[0] == 5:
	print("File not found.")
	exit()
else:
	List = Answer.split(b)
	if Opcode_rec[0] == 6:
		SIZE = int(List[2])
	else:
		SIZE = 1

#Creating file for writing:
fil = open(My_filename, 'w+')
m = hashlib.md5()


#Connection Loop:
while 1:
	End = 0
	Message = Ack + pack('!H', Order % 65536)
	sock.sendto(Message, Adr)
	while 1:
		try:
			Answer, adr = sock.recvfrom(1024)
			if adr != Adr:
				continue
			if unpack('!H', Answer[:2])[0] != 3:
				continue
			if unpack('!H', Answer[2:4])[0] <= Order:
				continue
			break
		except socket.timeout:
			sock.sendto(Message, Adr)
	if unpack('!H', Answer[2:4])[0] > Order + 1:
		continue
	else:
		Order = (Order + 1) % 65536
		Data = Answer[4:]
		fil.write(Data)
		m.update(Data)
		if len(Data) < 512:
			Message = Ack + pack('!H', Order % 65536)
			iterat = 0
			while 1: #Trying to help server with ending
				try:
					Answer, adr = sock.recvfrom(1024)
					sock.sendto(Message, Adr) 
				except socket.timeout:
					iterat += 1
					if iterat == 10:
						break
			break
			
	for i in range(0, SIZE - 1):
		try:
			Answer, adr = sock.recvfrom(1024)
			if adr != Adr:
				continue
			if unpack('!H', Answer[:2])[0] != 3:
				continue
			if unpack('!H', Answer[2:4])[0] <= Order:
				continue
		except socket.timeout:
			break
		if unpack('!H', Answer[2:4])[0] > Order + 1:
			break
		else:
			Order = (Order + 1) % 65536
			Data = Answer[4:]
			fil.write(Data)
			m.update(Data)
			if len(Data) < 512:
				Message = Ack + pack('!H', Order % 65536)
				iterat = 0
				while 1: #Trying to help server with ending
					try:
						Answer, adr = sock.recvfrom(1024)
						sock.sendto(Message, Adr) 
					except socket.timeout:
						iterat += 1
						if iterat == 10:
							End = 1
							break
				break
	if End == 1:
		break	
	
#Printing md5:
print(m.hexdigest())
