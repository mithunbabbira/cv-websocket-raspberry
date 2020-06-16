import cv2
import numpy as np 
from pynput.mouse import Button, Controller
import wx
import socket
import time


HEADERSIZE = 10

# ipv4 , tcp
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((socket.gethostname(),2650))
s.listen(5)


mouse = Controller()


# initializing app in wx , but false because we are not using it 
app = wx.App(False)
(sx,sy) = wx.GetDisplaySize()


#HSV color range
lowerBound = np.array([143,90,115])
upperBound = np.array([179,255,255])

cam = cv2.VideoCapture(0)

# to window size
(camx,camy)=(320,420)
cam.set(3,camx)
cam.set(4,camy)


# morphology to remove the noise
kernelOpen = np.ones((5,5))
kernelClose = np.ones((20,20))

pinchFlag=0 
m = 1 


# not used yet 
DampingFactor = 5 # shpuld be > 1
#mouseLoc = mouseLocOld + (targetLoc-mouseLocOld)/DampingFactor

co = 0


while True:
	clientsocket , address = s.accept()
	print (f"Connection from {address} has been established!")

	msg = "00"
	msg = f'{len(msg):<{HEADERSIZE}}'+ msg

	clientsocket.send(bytes(msg,"utf-8"))
	print("coming")
	

	while True:
		ret, img = cam.read()
		img = cv2.flip(img,1)
		imgHSV = cv2.cvtColor(img,cv2.COLOR_BGR2HSV)
		# Create a mask
		mask = cv2.inRange(imgHSV,lowerBound,upperBound)
		#morphology
		maskOpen = cv2.morphologyEx(mask,cv2.MORPH_OPEN,kernelOpen)
		maskClose = cv2.morphologyEx(maskOpen,cv2.MORPH_CLOSE,kernelClose)

		maskFinal = maskClose
		Contour, h = cv2.findContours(maskFinal.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)



		if(len(Contour)==2):
			if(pinchFlag==1):
				pinchFlag = 0
				mouse.release(Button.left)


			x1,y1,w1,h1 = cv2.boundingRect(Contour[0])
			x2,y2,w2,h2 = cv2.boundingRect(Contour[1])
			cv2.rectangle(img,(x1,y1),(x1+w1,y1+h1),(255,0,0),2)
			cv2.rectangle(img,(x2,y2),(x2+w2,y2+h2),(255,0,0),2)

			# line coot=rdinates 


			cx1=x1+w1/2
			cy1=y1+h1/2
			cx2=x2+w1/2
			cy2=y2+h2/2#mid point
			cx=(cx1+cx2)/2
			cy=(cy1+cy2)/2
			cv2.line(img,(int(cx1),int(cy1)),(int(cx2),int(cy2)),(255,0,0),2)
			cv2.circle(img,(int(cx),int(cy)),2,(0,0,255),2)
			mouseLoc=(sx-(cx*sx/camx),cy*sy/camy)
			mouse.position=mouseLoc
			openX,opneY,openW,openH=cv2.boundingRect(np.array([[[x1,y1],[x1+w1,y1+h1],[x2,y2],[x2+w2,y2+h2]]]))#draw rectangle
			cv2.rectangle(img,(openX,opneY),(openX+openW,opneY+openH),(0,0,255),2)




		elif(len(Contour)==1):


			x,y,w,h=cv2.boundingRect(Contour[0])#if(pinchFlag==0):#pinchFlag=1#mouse.press(Button.left)
			x,y,w,h=cv2.boundingRect(Contour[0])
			cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
			cx=x+w/2
			cy=y+h/2
			tem=(w+h)/4
			cv2.circle(img,(int(cx),int(cy)),int(tem),(0,0,255),2)

			co = int(cx)
			#print(int(cx))#mouse.position=(sx-(cx*sx/camx),cy*sy/camy)
			mouseLoc=(sx-(cx*sx/camx),cy*sy/camy)
			mouse.position=mouseLoc


		print("inside")
		time.sleep(.1)
		
		msg=f"{co}"
		msg=f'{len(msg):<{HEADERSIZE}}'+msg
		clientsocket.send(bytes(msg,"utf-8"))


		cv2.imshow("cam",img)
		cv2.imshow("contour",maskFinal)
		k=cv2.waitKey(1)
		if k == 27:
			break



cam.release()
cv2.destroyAllWindows()


















