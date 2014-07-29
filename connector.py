import time
import urllib

while True:
	
	time.sleep(100)
	urllib.urlopen("http://www.google.com").read()

