import socket
import threading
import os

BUFFER_SIZE = 1024
NUM_USERS = 10

client_queue = dict()

#get the port number from the user
port_check = True
while (port_check):
	port_input = input('Port number: ')
	try:
		port = int(port_input)
	except Exception as e:
		print("Please enter the port in numbers.")
		continue			
	if(port > 1024 and port < 65535):
		port_check = False

#create the socket
sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockfd.bind(('',port)) 

print("Sever is on.")
		
def Socket_Thread():

	# create the socket we are going to recieve from
	connected_socket, addr = sockfd.accept()

	while True:
		data = connected_socket.recv(BUFFER_SIZE)

		#if there is anything in the message
		if(data):
			printable = data.decode()

			#if it is a special request
			if(printable[0] == '~'):

				#requested client list
				if('clientlist' in printable):
					print("asked for list")

					#create the client list
					client_list = printable + '~'
					for elm in client_queue.values():
						client_list = client_list + elm + '~'

					#send the list
					send_val = str.encode(client_list)
					connected_socket.send(send_val)

				#sent a username
				elif('username' in printable):

					#parse out the username
					username_location = (printable.rfind('~') + 1)
					username = printable[username_location:]
					print("New user: "+ username)

					# update the list of clients
					client_queue[connected_socket] = username

				#attempted to send a pm
				elif('privatemessage' in printable):

					#parse out message and dest
					printable = printable.replace("~privatemessage~","")
					tl = printable.find('~')
					username = printable[0:tl]
					message = printable[(tl+1):]

					response = "Message sent to "+username

					#if valid username send it
					if username not in client_queue.values():
						response = "Message not sent. " + username +" not a valid recepiant."
					else:
						for socket, name in client_queue.items():
							if name == username:
								print("private message sent")
								socket.send(str.encode(message + "~Private " + client_queue[connected_socket]))

						connected_socket.send(str.encode(response))

				#kick user request
				elif('kickuser' in printable):

					#parse out info
					printable = printable.replace("~kickuser~","")
					tl = printable.find('~')
					username = printable[0:tl]
					message = "~kicked~" + printable[(tl+1):]
					response = "Kicked user "+username

					#if valid user, turn off their terminal
					# remove from client list
					if username not in client_queue.values():
						print("user " + username + "kicked")
						response = "User not kicked. " + username +" is not a valid user."
					else:
						for socket, name in client_queue.items():
							if name == username:
								socket.send(str.encode(message))
								del client_queue[connected_socket]
								break
						connected_socket.send(str.encode(response))
						continue
			else:

				#if they exited the program 
				if(printable.lower() == 'quit'):
					print("Client disconnected.")
					del client_queue[connected_socket]

				#any thing else is a valid message
				else:
					print(client_queue[connected_socket] + " > " + printable)
					#if there are any clients
					if client_queue:
						#send the message to all clients
						for client_sock in client_queue.keys():
							if client_sock != connected_socket:
								#append with user name
								client_sock.send(str.encode(printable + "~" + client_queue[connected_socket]))

#allow for up to ten users
sockfd.listen(NUM_USERS)
for itr in range(NUM_USERS):
	#create the socket thread, make sure daemon is false, so we can keep running
	sock_thread = threading.Thread(target = Socket_Thread)
	sock_thread.daemon = False
	sock_thread.start()
