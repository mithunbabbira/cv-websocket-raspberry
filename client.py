import socket
import RPi.GPIO as GPIO
import time


stg = ""
res = 0 
HEADERSIZE = 10

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("192.168.43.192",2650))

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(11,GPIO.OUT)
servo = GPIO.PWM(11, 50)
servo.start(0)


while True:
	full_msg = ''
	new_msg = True
	while True:
		msg = s.recv(16)
		if new_msg:
			# print(f"new message lenght: {msg[:HEADERSIZE]}")
			msglen = int(msg[:HEADERSIZE])
			new_msg = False


		full_msg += msg.decode("utf-8")

		if len(full_msg)-HEADERSIZE == msglen:
			print("full msg recvd")
			res = int(full_msg[5:])
			angle = res/2
			servo.ChangeDutyCycle(2+(angle/18))
			#time.sleep(0.5)
			
			print(angle)
			new_msg = True
			full_msg = ''

	