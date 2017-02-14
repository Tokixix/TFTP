#!/usr/bin/env python
import socket
import sys
import os.path
from struct import *
import threading

PORT = sys.argv[1]
PATH = sys.argv[2]
HOST = ''
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, int(PORT)))

class Sender(threading.Thread):
	
	def __init__(self, Message, addr, timeout):
		threading.Thread.__init__(self)
		self.Message = Message
		self.addr = addr
		
	def run(self):
		Time = 0
		Block = 1 #Block which we are about to send
		sock2 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock2.settimeout(0.1)
		b = pack('!B', 0)
		Opcode = self.Message[:2]
		iter = 2
		
		while 1:
			if self.Message[iter] == pack('!B', 0):
				break
			iter += 1
			
		Filename = self.Message[2:iter]
		F_Name = PATH + '/' + Filename
		
		if os.path.isfile(F_Name) == False:
			Opcode = pack('!H', 5)
			ErrorCode = pack('!H', 1)
			ErrorMsg = "File not found"
			self.Message = Opcode + ErrorCode + ErrorMsg + b
			sock2.sendto(self.Message, self.addr)
		else:
			File = open(F_Name, 'r')
			while 1:
				Data = File.read(512)
				Opcode = pack('!H', 3)
				self.Message = Opcode + pack('!H', Block) + Data
				sock2.sendto(self.Message, self.addr)
				
				while 1:
					try:
						Get, self.addr = sock2.recvfrom(1024)
						if unpack('!H', Get[2:])[0] == Block:
							Block = (Block + 1) % 65536
							break
					except socket.timeout:
						Time += 1
						if Time == 50:
							Time = -1
							break
						sock2.sendto(self.Message, self.addr)
						
				if Time == -1:
					break
				Time = 0
				if len(Data) < 512:
					break
while 1:
	Message, addr = sock.recvfrom(1024) #Got RRQ message 
	try:
		Sender(Message, addr, 0.1).start()
	except Exception:
		pass


