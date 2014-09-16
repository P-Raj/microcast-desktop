
import threading
import dmtcp



def func(p):
	for i in range(4):
		print p , ":" , i**p

t = None
for i in range(30):
	if i==5:
		t= threading.Thread(target=func,args=[2])
		t.start()
	if i==7:
		print dmtcp.checkpoint()

	
	#print "A"+str(i)
t.join()
