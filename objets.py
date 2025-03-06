from triangulation import great_circle_distance
from pythonping import ping

#########
# Landmark object
#########
class Landmark :
    name = ""
    latitude = 0
    longitude = 0
    adress = ""

    def __init__(self, n, lat, long, adr, i):
        self.name = n
        self.id = i
        self.latitude = lat
        self.longitude = long
        self.adress = adr

    def coordonnees(self) :
        return (self.latitude, self.longitude)

    def distance(self, point):
        if isinstance(point, Landmark):
            return great_circle_distance(self.latitude, self.longitude, point.latitude, point.longitude)
        else :
            return great_circle_distance(self.latitude,self.longitude, point[0], point[1])


    #def ping functions to Landmark (currently not used)
    def ping_avg_ms(self, c = 3, payload = 64):
        response = ping(self.adress, size = payload, count = c)
        #print("RTT avg ms ",self.name," : ",response.rtt_avg_ms)
        return response.rtt_avg_ms
    
    def ping_min_ms(self, c = 3, payload = 64):
        response = ping(self.adress, size = payload, count = c)
        #print("RTT min ms ",self.name," : ",response.rtt_min_ms)
        return response.rtt_min_ms
    
    def ping_avg_min_max(self, c = 3, payload = 64):
        response = ping(self.adress, size = payload, count = c)
        #print(response)
        #print((response.rtt_avg_ms,response.rtt_min_ms,response.rtt_max_ms))
        return (response.rtt_avg_ms,response.rtt_min_ms,response.rtt_max_ms)
