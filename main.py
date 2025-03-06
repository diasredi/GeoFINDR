import csv #useless
#code files
import choixlm
import distance_delai
#import necessary environment values
from environment_values import tolerance, zone_size, sector_lm_nb, declared_position, real_latitude, real_longitude, interval_percent
import recup_liste_lm
import triangulation
import time
import math



########
# GET LM list
########

landmarks_source = recup_liste_lm.import_landmarks()
landmarks = landmarks_source


print("\n---------------------------")
print(" NEW POSITION ESTIMATION :")
print("---------------------------\n")


print("Declared position : ", declared_position)

initial_position = declared_position

size_min_zone = 0

latest_sector = initial_position

start_time = time.time()
for nb_iterations in range(15):


	#PART 1 SECTOR ESTIMATION
	print("Sector estimation STEP ",nb_iterations,"\n--------\n")

	#near landmarks for triangulation : def landmarks_proches(landmarks, nombre, zone_size, declared_position)
	#return nb_zone to get number of available LMs in zone_size around position
	nearest_landmarks, nb_zone = choixlm.landmarks_proches(landmarks, sector_lm_nb, zone_size, initial_position, size_min_zone)

	#if not enough LMs in zone, extend zone
	while nb_zone < sector_lm_nb:
		
		zone_size = zone_size + tolerance
		nearest_landmarks, nb_zone = choixlm.landmarks_proches(landmarks, sector_lm_nb, zone_size, initial_position, size_min_zone)

	print(nb_zone, "landmarks in zone of ", zone_size, "km, for sector estimation")

	#choice dispersed LMs among nearest : def choix_lm(landmarks, nombre)
	selected_landmarks = choixlm.choix_lm(nearest_landmarks, sector_lm_nb)
	print("choosen landmarks : ",[lm.name for lm in selected_landmarks])

	#find the number of probes occurences>1
	included = distance_delai.corresponding_landmarks_delays(selected_landmarks,landmarks)
	
	#counting results
	dict_results = {-1:0} 
	for elem in included :
		for e in elem:
			if e in dict_results:
				dict_results[e] = dict_results[e]+1
			else:
				dict_results[e] = 1

	#Error if no result found
	print("number of failed measures ",dict_results[-1])
	if sector_lm_nb-dict_results[-1]<1 :
		print("Failed sector estimation not enough valid measures")

	#sort results by most similar
	sorted_results = dict(sorted(dict_results.items(), key=lambda x:x[1], reverse=True))
	print(sorted_results)
	fails = sorted_results.pop(-1)

	#obtaining the list of most similar anchors ID
	max_key_id = max(sorted_results, key=lambda key: sorted_results[key])

	correlated_ids = [key for key in sorted_results if sorted_results[key]==sorted_results[max_key_id] and key!=-1]
	print("\nID(s) of most similar anchors : ",[lm.name for lm in distance_delai.get_landmark_objects_from_ids(correlated_ids, landmarks)])
	print("Coefficient of similarity (occurrences / number of tests) : ",sorted_results[max_key_id]/(sector_lm_nb-fails))

	#sector position = average of similar anchors position A MODIFIER
	#th = ((sector_lm_nb-dict_results[-1])/2)-2
	#if sorted_results[max_key_id]<th:
	#	th = sorted_results[max_key_id]-1
	th = sorted_results[max_key_id]-1
	sector_lat, sector_long = distance_delai.weighted_average_position(sorted_results,landmarks,threshold=th) 
	#sector position is baricenter
	lms = distance_delai.get_landmark_objects_from_ids(correlated_ids, landmarks)
	sector_lat, sector_long, distances, eqm = distance_delai.find_baricenter(lms)
	print("baricenter values : ",(distances,eqm))


	print("new estimated sector : (", sector_lat,", ", sector_long,")")
	
	#if positions converges, continue
	if triangulation.great_circle_distance(latest_sector[0],latest_sector[1], sector_lat, sector_long)<tolerance:
		break
	else:
		#else try again with new position
		initial_position = (sector_lat,sector_long)
		latest_sector = initial_position

end_time = time.time()

#Display results in console : position, distance declared position (SLA respected ?), uncertain delay, reqm
print("\n---------------------------")
print(" WRAP UP :")
print("---------------------------\n")
audit_time = end_time-start_time
print("TIME OF AUDIT = ", audit_time)

print("Declared position in SLA : ",declared_position)

print("\nTolerance = ",tolerance,"; Zone's size = ",zone_size, "; Number of choosen landmarks = ",sector_lm_nb, "; Selected delay interval percent  = ",interval_percent)

print("\nRESULTS :")
print("-----------\n")


#sector position 
print("Sector position : (", sector_lat,", ", sector_long,")\n")
print("ID(s) of most similar anchors : ",correlated_ids)
print("Coefficient of similarity (occurrences / number of tests) : ",sorted_results[max_key_id]/(sector_lm_nb-dict_results[-1]))
print("Number of for latest estimation : ", dict_results[-1])
print("Number of iterations : ",nb_iterations+1)



#EXPERIMENT, if the real latitude and longitude are set, display the distance between real position and estimated sector
if real_latitude != None and real_longitude != None:
	real_position = (real_latitude, real_longitude)
	dist_estimation_real = triangulation.great_circle_distance(real_position[0], real_position[1], sector_lat, sector_long)
	print("EXPERIMENTAL : distance beetween real and sector position in km : ",dist_estimation_real)
	
	#dist_estimation_declared,eqm = 0,0
	dist_estimation_declared = triangulation.great_circle_distance(sector_lat, sector_long,declared_position[0],declared_position[1])
	print("EXPERIMENTAL : distance beetween declared and estimated position in km : ",dist_estimation_declared)

	anchors_paris = ['6921','6981','6960','6830','6333','6846','6666','6728','7042','7134','7067','7286','7146','6817', '6564', '7202']
	print("anchors en region parisienne selectionnes : ", [i for i in correlated_ids if str(i) in anchors_paris])
	print("anchors pas en region parisienne selectionnes : ", [i for i in correlated_ids if str(i) not in anchors_paris])

	path_results = r"resultats_initialEU.csv"
	dist_real_declared = triangulation.great_circle_distance(real_position[0], real_position[1], declared_position[0],declared_position[1])
	new_line = [declared_position[0],declared_position[1],dist_real_declared,dist_estimation_declared,dist_estimation_real,eqm ]#,capital[0]]
	
	with open(path_results,'a') as f:
		writer = csv.writer(f,delimiter=',')
		if nb_iterations == 0 :
				writer.writerow(["latitude","longitude","dist_real_declared","dist_estimation_declared","dist_estimation_real","eqm","nb_iterations","capitale"])
		writer.writerow(new_line)
