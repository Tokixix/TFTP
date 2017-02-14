#!/usr/bin/env python
import socket
import sys
import os.path
from struct import *
import threading

#Preparing for the connection:
PORT = int(sys.argv[1])
PATH = sys.argv[2]
HOST = ''
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, int(PORT)))

class Sender(threading.Thread):
	
	def __init__(self, Message, addr, timeout):
		threading.Thread.__init__(self)
		self.daemon = True
		self.Message = Message 
		self.addr = addr
		self.Block = 0
		self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		self.sock.settimeout(timeout)
		self.Ack = 0
		
	def run(self):

		#Informations about winsize:
		b = pack('!B', 0)
		List = self.Message.split(pack('!B', 0))
		Filename = List[1][1:]
		F_Name = PATH + '/' + Filename
		size = int(List[4])
		
		if os.path.isfile(F_Name) == False:
			Opcode = pack('!H', 5)
			ErrorCode = pack('!H', 1)
			ErrorMsg = "File not found."
			self.Message = Opcode + ErrorCode + ErrorMsg + b
			self.sock.sendto(self.Message, self.addr)
			
		else:
			self.Message = self.Message = pack('!H', 6) + str(size) + b + str(size) + b
			self.sock.sendto(self.Message, self.addr) 
			Time = 0
			while 1: #Sending 0ACK to user
				try:
					Answer, addr = self.sock.recvfrom(1024) #waitning for Ack0 to start
					if unpack('!H', Answer[2:])[0] == self.Block:
						self.Block = (self.Block + 1) % 65536
						break
					else:
						self.sock.sendto(self.Message, self.addr) 
				except socket.timeout:
					Time += 1
					if Time == 50:
						exit()
					self.sock.sendto(self.Message, self.addr)
	
			File = open(F_Name, 'r') #File of out Data
			Packs = [i for i in range(0, size)] #List for "size" of packages
			iterate = 0 #place from which we start creating new packets
			last = size #variable set for last packet which should be sent
			lost = 0 #couting ammount od lost packets
			Last = -1 #number of Last packet
			Time = 0 #Checking if client is ok
			while 1:
				if Last == -1:
					for i in range(iterate, size):
						Data = File.read(512)
						Opcode = pack('!H', 3)
						Message = Opcode + pack('!H', self.Block) + Data
						Packs[i] = Message
						self.Block = (self.Block + 1) % 65536
						if len(Data) < 512:
							last = i + 1
							Last = (self.Block - 1) % 65536
							break
						
				#sending all messages
				for i in range(0, last):
					self.sock.sendto(Packs[i], self.addr)
					
				while 1:
					try:
						Answer, adr = self.sock.recvfrom(1024)
						Time = 0
						Ack = unpack('!H', Answer[2:])[0]
						if Ack <= self.Ack: #we are sure that we got that earlier
							continue
						else:
							self.Ack = Ack
							if Last == -1:
								lost = self.Block - Ack - 1
								Temp = [x for x in range(0,size)]
								for i in range(0, lost): #Translation of fine messages
									Temp[i] = Packs[-lost + i]
								Packs = Temp 
								iterate = lost #Now we start reading new packets from this place
							break
						
					except socket.timeout:
						Time += 1
						if Time == 50:
							exit()
						iterate = size
						break
						
				if((self.Ack) % 65536 == Last):
					break

while 1:
	Message, addr = sock.recvfrom(1024) #Got RRQ message 
	try:
		Sender(Message, addr, 0.1).start()
	except Exception:
		pass
	
