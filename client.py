import socket
import threading
import ipaddress
import os

BUFFER_SIZE = 1024
PASSWORD = "1234"

#User input the port num
port_check = True
while (port_check):
	port_input = input('Port number: ')
	try:
		port = int(port_input)
	except Exception as e:
		print("Please enter the port in numbers.")
	if(port > 1024 and port < 65535):
		port_check = False

#user input the IP address
ip_check = True
while(ip_check):
	ip = input('Destination IP: ')
	try:
		ipaddress.ip_address(ip)
		ip_check = False
	except Exception as e:
		print("Please enter a valid IP address.")

user_name = ""

#determine the source of the server
dest = (ip,port)

#create the socket
sockfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sockfd.connect((dest))

#when the user wants to see the menu
def User_Menu():
	while(True):

		Print_Menu()
		ui = input("> ")

		#validate input
		try:
			menu_selection = int(ui)
		except Exception as e:
			print("Please Enter a valid input\n") 
			continue
		if(menu_selection<1 or menu_selection>5):
			print("Please Enter a valid input\n") 
			continue
		else:
			#client list
			if menu_selection == 1:
				request = "~clientlist"
				send_val =str.encode(request)
				sockfd.send(send_val)
			#PM
			elif menu_selection == 2:
				target = input('Target username > ')
				message = input('Message > ')
				request = "~privatemessage~"+target+'~'+message
				send_val =str.encode(request)
				sockfd.send(send_val)
			#admin menu
			elif menu_selection == 4:
				Print_Admin()
			#quit program
			elif menu_selection == 5:
				sockfd.send(str.encode("quit"))
				os._exit(0)
			break	

#Print the user menu
def Print_Menu():
	print("\n========== Menu ==========\n"+
			"1. List of clients\n"+
			"2. Message client\n"+
			"3. Message all clients\n"+
			"4. Admin Menu\n"+
			"5. exit\n")

#print and run the admin menu
def Print_Admin():
	print("===Admin Menu===")
	ctr = 0
	while(True):
		pwa = input("Password > ")
		#password checking
		if(pwa != PASSWORD):
			ctr = ctr + 1
			if(ctr > 2):
				print("Password failed goodbye")
				return()
			else:
				print("Password failed try again")
		else:
			while(True):
				#input validation
				print("1. Kick client\n" + 
					"2. Exit\n")
				ai = input("\n> ")
				try:
					selection = int(ai)
				except Exception as e:
					print("Please Enter a valid input\n") 
					continue
				if(selection<1 or selection>2):
					print("Please Enter a valid input\n") 
					continue
				#kick user
				if(selection == 1):
					target = input('Kick user > ')
					message = input('Reason > ')
					request = "~kickuser~"+target+'~'+message
					send_val =str.encode(request)
					sockfd.send(send_val)
					return()
				#leave menu
				elif(selection == 2):
					return()
			break

#send a username to the server
def New_Username():
	user_name = input("User name > ")
	message = "~username~" + user_name
	sockfd.send(str.encode(message)) 

#the function that the socket recevie thread will run
def Socket_Thread():
	New_Username()
	print("Connected to server on a public chanel.")
	print("Type 'menu' to see options.")

	while True:

		#users raw message
		data = sockfd.recv(BUFFER_SIZE)

		#readable message
		printable = data.decode()
		
		#if you were sent a special request
		if(printable[0] == '~'):

			#print the client list
			if("clientlist" in printable):
				printable = printable.replace('~','\n')
				print(printable)

			#Youve been kicked
			elif("kicked" in printable): 
				printable = printable.replace("~kicked~","")
				print("You have been kicked.")
				print("Admin reason: " + printable)
				os._exit(0)

		#print users message
		else:
			tl = printable.find('~')
			other_username = "Server"
			if(tl > 0):
				other_username = printable[(tl+1):]
				printable = printable[0:tl]

			#if the message was quit, quit
			if(printable.lower() == 'quit'):
				print("Server disconnected. Goodbye.")
				os._exit(0)

			print("["+other_username + "] " + printable)

#the function that our input will run
def Input_Thread():
	while True:
		#read message
		message = input("\n")
		text_message = str.encode(message)

		#if the message was quit, quit
		if(message.lower() == 'quit'):
			sockfd.send(text_message)
			print("\nClient disconnected.")
			os._exit(0)

		#print the menu options
		elif(message.lower() == 'menu'):
			User_Menu()

		#send user message
		else:
			sockfd.send(text_message )

#create the socket thread, make sure daemon is false, so we can keep running
sock_thread = threading.Thread(target = Socket_Thread)
sock_thread.daemon = False

#create the input thread
input_thread = threading.Thread(target = Input_Thread)
input_thread.daemon = False

sock_thread.start()
input_thread.start() 