import math
from scipy.optimize import minimize, minimize_scalar


#great circle distance compute beetween A and B
#source : https://www.alanzucconi.com/2017/03/13/understanding-geographical-coordinates/
def great_circle_distance (latitudeA, longitudeA, latitudeB, longitudeB):
    # Degrees to radians
    phi1    = math.radians(latitudeA)
    lambda1 = math.radians(longitudeA)
    phi2    = math.radians(latitudeB)
    lambda2 = math.radians(longitudeB)
    delta_lambda = math.fabs(lambda2 - lambda1)
    central_angle =math.atan2(# Numerator
            math.sqrt(# First
                math.pow
                (math.cos(phi2) * math.sin(delta_lambda), 2.0)+
                # Second
                math.pow(math.cos(phi1) * math.sin(phi2) -math.sin(phi1) * math.cos(phi2) * math.cos(delta_lambda), 2.0)),
                # Denominator
            (math.sin (phi1) * math.sin(phi2) +math.cos (phi1) * math.cos(phi2) * math.cos(delta_lambda)))
    R = 6371.009 # Km
    return R * central_angle



########
#intersection calculus
########

#triangulation
#takes landmarks list, their respective distances to the target and an initial position (impacts result, calculation speed and estimation)
#source : https://www.alanzucconi.com/2017/03/13/positioning-and-trilateration/
def estimation_position(locations, distances, initial_location = [0,0]):

    
    #function to calculate Squared Mean Error SME (erreur quadratique moyenne EQM)
    def eqm(x, locations, distances):
        eqm = 0.0
        for location, distance in zip(locations, distances):
            distance_calculated = great_circle_distance(x[0], x[1], location.coordonnees()[0], location.coordonnees()[1])
            eqm += math.pow(distance_calculated - distance, 2.0)
        return eqm / len(distances)

    
    # SME minimisation. Note that the solution doesn't necesseraly converges, but the difference is often negligeable
    result = minimize(eqm,initial_location,args=(locations, distances),method='L-BFGS-B',options={'ftol':1e-5,'maxiter': 1e+7})

    #results extraction
    lat_opt,lon_opt = result.x
    incertitude = eqm((lat_opt,lon_opt),locations,distances)


    #return position estimation and incertitude (Squared Mean Error)
    return (float(lat_opt),float(lon_opt),incertitude)




# EXPERIMENTATION

def position_multilateration(locations,delays,initial_location = [0,0]):
    d=0
    max_delay = max(delays)
    coeffs_distances = [d/max_delay for d in delays]
    
    #coeffs_distances = [1]*len(coeffs_distances)
    
    def positions_baricenter(d):
        distances = [d*c for c in coeffs_distances]

        #function to calculate Squared Mean Error SME (erreur quadratique moyenne EQM)
        def eqm(x, locations, distances):
            eqm = 0.0
            for location, distance in zip(locations, distances):
                distance_calculated = great_circle_distance(x[0], x[1], location.coordonnees()[0], location.coordonnees()[1])
                eqm += math.pow(distance_calculated - distance, 2.0)
            return eqm / len(distances)


        # SME minimisation. Note that the solution doesn't necesseraly converges, but the difference is often negligeable
        result = minimize(eqm,initial_location,args=(locations, distances),method='L-BFGS-B',options={'ftol':1e-5,'maxiter': 1e+7})

        #results extraction
        lat_opt,lon_opt = result.x
        incertitude = eqm((lat_opt,lon_opt),locations,distances)

        #return position estimation and incertitude (Squared Mean Error)
        return incertitude


    sol = minimize_scalar(positions_baricenter)
    print("valeur retour : ",sol.fun)
    print("valeur d : ",sol.x)

    d = sol.x
    distances = [d*c for c in coeffs_distances]
    lat_opt,lon_opt,incertitude = estimation_position(locations, distances, initial_location)
    

    return distances, lat_opt, lon_opt, incertitude