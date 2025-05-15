import json
from dotenv import dotenv_values
import public_ip
from pythonping import ping

########
# environment variables
########


# environment variables in json
#with open('environment_values.json', 'r') as file:
#    env_values = json.load(file)

#load .env variables
env_values = dotenv_values(".env")
print(env_values)

tolerance = float(env_values['tolerance']) #tolerance or acceptable error distance
zone_size = float(env_values['zone_size']) #search zone initial size
sector_lm_nb = int(env_values['sector_lm_nb']) #number of landmarks to select for sector estimation



########
# GET declared region SLA / VM
########

declared_position = (float(env_values['declared_latitude']),float(env_values['declared_longitude']))


########
# GET public IP / proxy
########

loopback = env_values['loopback_adress'] #default "127.0.0.1"

#GET proxy address or set if known
try:
	if env_values['proxy_adress']==None:
		proxy_addr = public_ip.get() #https://pypi.org/project/public-ip/
	else:
		proxy_addr = env_values['proxy_adress']

	if not ping(proxy_addr, count = 1).success():
		proxy_addr = loopback
except:
	proxy_addr = loopback
	print("proxy is set to loopback")

print("PROXY IP ADDRESS : ",proxy_addr)


#######
# Data analysis variables
#######

interval_percent = float(env_values['interval_percent'])/100


#######
# Experimental values
#######
real_latitude = float(env_values['real_latitude'])
real_longitude = float(env_values['real_longitude'])