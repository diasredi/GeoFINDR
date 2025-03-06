from pythonping import ping
from ripe.atlas.cousteau import AtlasRequest
from ripe.atlas.cousteau import AtlasLatestRequest

#import matplotlib.pyplot as plt #display only

from environment_values import proxy_addr, loopback, interval_percent
from triangulation import position_multilateration





##########
# Find sector of the computer using mesured delays, and counting the landmarks corresponding the most to our computer behavior
##########
# Get measurements
# For a measured delay, find anchors in the delay interval


def corresponding_landmarks_delays(selected_landmarks, landmarks,interval_percent=interval_percent):
	loopbackRTT,proxyRTT,localRTT = 0,0,0
	 

	#list of anchors included in the delay interval for each selected_landmark
	included = []
	
	for lm in selected_landmarks :
		#try:
		#if first ping doesn't work then skip test and add error
		if ping(lm.adress, size = 1, timeout = 1, count = 1).success()==False: 
			included.append([-1])
			continue


		#find msm_id for the lm
		msm_id = find_msm_id(lm.id)
		if msm_id == -1:
			included.append([-1])
			continue


		#find probes involved in measurement and adequat payload and counts
		res = find_participants(msm_id)
		if res==-1:
			included.append([-1])
			continue

		involved_probes_ids, payload, counts = res

		print("Anchor ID : ",lm.id)
		print("Payload and number of pings : ",payload," & ",counts)


		#FILTER involved probes
		involved_probes_ids = valid_ids(involved_probes_ids,landmarks)
		involved_probes_ids =  [str(l.id) for l in get_landmark_objects_from_ids(involved_probes_ids,landmarks) ]#if l.distance(lm)<500]



		#IN CLOUD DISTANCES
		#we calculate mean RTT processing of pings by the VM (sending+reception) by pinging loopback adress
		#we calculate mean RTT beetween VM and PROXY by pinging public IP /!/ blocks often pings
		#the sum of both RTT's allows us to define an incertitude "in-cloud", removed to ping's total RTT. Allows to get internet's RTT


		loopbackRTT = ping(loopback, size = payload, count = counts)
		print("loopbackRTT : ",loopbackRTT.rtt_min_ms)

		proxyRTT = ping(proxy_addr, size = payload, timeout = 1, count = counts)
		print("proxyRTT : ", proxyRTT.rtt_min_ms)

		
		#localRTT, treatment delay beetween PROXY and VM, becomes incertitude
		localRTT = loopbackRTT.rtt_min_ms
		if proxyRTT.success():
			localRTT = proxyRTT.rtt_min_ms #if PROXY's RTT is mesured it becomes localRTT because includes loopbackRTT
			proxyRTT = proxyRTT.rtt_min_ms
		else :
			proxyRTT = -1 #otherwise not mesurable



		#mesured delay to anchor
		response = ping(lm.adress, size = payload, timeout = 1, count = counts) #ping LM

		if response.success(): #if ping success, get speeds (distance / delay relation) of LM

			mesured_delay = response.rtt_min_ms-localRTT #measured delay

			#Definition of delay interval +- 10% of mesured minimum
			mesured_min = (1-interval_percent)*(response.rtt_min_ms - localRTT)
			mesured_min = max(0,mesured_min)

			mesured_max = (1+interval_percent)*(response.rtt_min_ms - localRTT)
			mesured_max = max(1,mesured_max)


			print("interval delay of ", lm.name," : [",mesured_min," ; ",mesured_max,"]")

			#get latest measurements values for the involved probes
			res = get_latest_measurements(msm_id, involved_probes_ids, str(lm.id), mesured_min,mesured_max)
			
			if res == -1:
				included.append([-1])
				continue

			relation_delays, associated_probes_id_result = res

			if len(relation_delays)==0 or len(associated_probes_id_result)==0:
				print("ERROR IN FETCHING MEASUREMENT RESULTS : skip")
				included.append([-1])
				continue

			involved_probes = get_landmark_objects_from_ids(associated_probes_id_result,landmarks)
			selected_ids = [str(p.id) for p in involved_probes]
			print("INVOLVED PROBES IDs in interval : ",selected_ids)
			included.append(selected_ids)


			print("Mesured delay : ",mesured_delay)
			
		else :
			included.append([-1])
		#except:
		#	print("Error in corresponding_landmarks_delays, landmark id  : ",lm.id)
		#	included.append([-1])	



	return included
	








########
# obtain msm_id of IPv4 mesh measures from an anchor id
########

def find_msm_id(anchor_id):
	url_path = "/api/v2/measurements/?tags=anchoring%2Cmesh&search="+str(anchor_id)+"&af=4&type=ping" #api returns measurements data
	request = AtlasRequest(**{"url_path": url_path})
	(is_success, response) = request.get()
	if not is_success :
		return -1

	try:
		return response['results'][0]['id'] #most common response
	except:
		return -1



########
# obtain all participants id in measurement
########

def find_participants(msm_id):
	url_path = "/api/v2/measurements/"+str(msm_id)+"/?optional_fields=current_probes"
	request = AtlasRequest(**{"url_path": url_path})
	(is_success, response) = request.get()
	if not is_success :
		return -1
	
	try:
		return response['current_probes'], response['size'], response['packets']
	except:
		return -1


#########
# get latest measurements results beetween an anchor and the participants (via msm_id)
#########

def get_latest_measurements(msm_id, participants, anchor_id, mesured_min=0,mesured_max=10000):

	kwargs = {
		"msm_id": msm_id,
		"probe_ids": [anchor_id]
	}

	is_success, results = AtlasLatestRequest(**kwargs).create()
	if is_success:
		internal_delay = results[0]['avg']
	else:
		internal_delay = 0




	kwargs = {
		"msm_id": msm_id,
		"probe_ids": participants
	}

	is_success, results = AtlasLatestRequest(**kwargs).create()
	if not is_success :
		return -1

	delay_results = []
	associated_probes_id_result = []

	try:	#filter failed measurements
		for r in results:
			if r['avg'] > 0 and r['avg'] > mesured_min and r['avg'] < mesured_max:
				delay_results.append(r['avg']-internal_delay)
				associated_probes_id_result.append(r['prb_id'])

		return delay_results, associated_probes_id_result

	except:
		return -1



#########
# filtering function, returns True if an ID is valid from a landmarks list
#########
def valid_ids(ids,landmarks):
	return [str(i) for i in ids if str(i) in [str(lm.id) for lm in landmarks]]




#######
# transform probe id list into landmark object list
#######
def get_landmark_objects_from_ids(ids,landmarks):
	result = []
	for i in ids :
		for lm in landmarks:
			if str(lm.id) == str(i):
				result.append(lm)
	return result


#######
# from a dictionnary associating a landmark and the number of occurences, returns the weighted average of the position
#######

def weighted_average_position(occurences_dict,landmarks,threshold = 1):
	denom = 0
	ids = []
	for e in occurences_dict:
		#skip -1 and values lower than 3
		if e != -1 and occurences_dict[e] > threshold :
			denom+= occurences_dict[e]**2
			ids.append(e)

	ids = get_landmark_objects_from_ids(ids,landmarks)

	lat,lon = 0,0
	for probe in ids:
		lat += probe.latitude*occurences_dict[str(probe.id)]**2
		lon += probe.longitude*occurences_dict[str(probe.id)]**2
		
	lat = lat/denom
	lon = lon/denom
			
	return lat,lon


def find_baricenter(landmarks):
	#landmarks = locations

	#mesure delais
	delays = [lm.ping_min_ms() for lm in landmarks]
	init_lat = sum([lm.coordonnees()[0] for lm in landmarks])/len(landmarks)
	init_long = sum([lm.coordonnees()[1] for lm in landmarks])/len(landmarks)

	distances, lat_opt, lon_opt, incertitude = position_multilateration(landmarks,delays,(init_lat,init_long))
	
	return lat_opt, lon_opt, [float(d) for d in distances], incertitude