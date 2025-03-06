import numpy as np
from triangulation import great_circle_distance


########
# LM choice
########

#chooses the n landmarks to use for triangulation around a position. 
#tolerance is the distance from which we consider a LM near enough.
def landmarks_proches(landmarks, number, zone_size, declared_position, min_zone_size = 0):

    #calculates distance in km (geodesic distance, 0,5% error)
    #distances beetween each landmarks and VM's declared position
    distances = [lm.distance(declared_position) for lm in landmarks]

    #the "number" smallest values indices in ascending order of distances
    ordered_landmarks = np.argsort(distances)#[:nombre]

    #we want "number" landmarks in the zone. zone_size is the initial number of available lm in the zone
    near = [landmarks[i] for i in ordered_landmarks if (distances[i]<zone_size and distances[i]>=min_zone_size)]
    nb_zone = len(near)

    #if there are not enough landmarks, we select the nearests
    if nb_zone<number:
        for i in ordered_landmarks[len(near):number]:
            near.append(landmarks[i])

    return near,nb_zone #returns nearest landmarks coordinates and the amount included in the zone




#function that chooses a number of dispersed LMs
def choix_lm(landmarks, nombre):
    #if the number of landmarks is equal to list's size, return all LMs
    if len(landmarks)<=nombre:
        return landmarks


    #greedy algorithm to select dispersed points :
    # 1) select n LMs (points)
    # 2) for each LM in landmarks replace it with the nearest selected LM
    # 3) if the sum of the distances is greater replace for the selected
    selected = landmarks[:nombre]
    
    for lm in landmarks[nombre:]:
        #distances beetween lm and selected
        distances = [great_circle_distance(lms.latitude,lms.longitude,lm.latitude,lm.longitude) for lms in selected]
        #nearest point from lm
        nearest_point = selected[ distances.index(min(distances)) ]

        #remove nearest point from selected to calculate the distances correctly
        selected.remove(nearest_point)


        #add to selected the landmark that maximises the distances with other selected points
        if sum([great_circle_distance(lms.latitude,lms.longitude,lm.latitude,lm.longitude) for lms in selected]) > sum([great_circle_distance(lms.latitude,lms.longitude,nearest_point.latitude,nearest_point.longitude) for lms in selected]):
            selected.append(lm)
        else :
            selected.append(nearest_point)
    
    return selected