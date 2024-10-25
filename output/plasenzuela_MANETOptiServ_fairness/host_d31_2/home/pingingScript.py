import time, threading, ping3, random
import pandas as pd
WAIT_SECONDS = 1 / 1.0
pings = []
time_reference = time.time()
duration = 60 
def ping_to_server():
	ping_time = time.ctime()
	rtt = ping3.ping('129.0.0.169')
	pings.append([ping_time, rtt])
def periodic_function():
	threading.Thread(target=ping_to_server()).run()
	if time.time() - time_reference < duration:
		threading.Timer(WAIT_SECONDS, periodic_function).start()
	else:
		time.sleep(random.randint(600, 1200) / 10.0)
		df = pd.DataFrame(data=pings, columns=['Ping timestamp', 'RTT'])
		df.to_csv('/shared/host_d31_2')
periodic_function()
