from urllib.request import urlretrieve
import bz2
import json
from objets import Landmark

########
# DEFINITION of a selectable landmark
########
def is_selectable(p):
    #MODIFY HERE TO CHANGE LANDMARKS MESH
    #anchors_paris = ['6921','6981','6960','6830','6333','6846','6666','6728','7042','7134','7067','7286','7146','6817', '6564', '7202']
    #if str(p['id']) in anchors_paris :
    #    return False
    #if p['longitude']==None:
    #    return False
    #if p['longitude'] > 2.5 or str(p['id']) in anchors_paris:
    #    return False
    
    return (p['address_v4']!=None and p['latitude']!=None and p['longitude']!=None and p['status_name']=='Connected' and p['is_anchor']==True)



########
# GET LM list from RIPE Atlas
########
#ideally landmarks import is not executed systematically, to not always download the archive and save bandwidth

def import_landmarks():
    #url to download up to date LMs list : https://ftp.ripe.net/ripe/atlas/probes/archive/meta-latest
    #shortcut to today's LMs list : https://ftp.ripe.net/ripe/atlas/probes/archive/AA/MM/AAMMJJ.json.bz2 avec jour-1
    url = "https://ftp.ripe.net/ripe/atlas/probes/archive/"
    file = ("meta-latest")
    
    #download file #https://docs.python.org/3/library/urllib.request.html
    urlretrieve(url+file,file)
    print("probes list obtained from RIPE Atlas")

    #unzip .json.bz2 type file https://docs.python.org/3/library/bz2.html
    with bz2.open(file, "rb") as f:
        fjson = f.read()


    #file format {"objects" : [liste des probes], "meta" : {'total_count': 37850, 'limit': 0, 'offset': None}}
    probes = json.loads(fjson)
    print("total number of probes : ", probes['meta']['total_count'])


    #we only keep probes that can be landmarks :
    # "address_v4","latitude","longitude" != Null and "status_name"=="Connected"
    #then we can name them with "id" and "country_code" for example

    landmarks = [Landmark(str(p['id'])+str(p['country_code']), p['latitude'], p['longitude'], p['address_v4'],p['id']) for p in probes['objects'] \
                if is_selectable(p)]
    print("number of selectable landmarks : ",len(landmarks))

    
    return landmarks


############
# GET landmarks list from local file
############

def import_file_landmarks(file):
    #unzip .json.bz2 type file https://docs.python.org/3/library/bz2.html
    with bz2.open(file, "rb") as f:
        fjson = f.read()


    #file format {"objects" : [liste des probes], "meta" : {'total_count': 37850, 'limit': 0, 'offset': None}}
    probes = json.loads(fjson)
    print("nombre total de probes : ", probes['meta']['total_count'])


    #we only keep probes that can be landmarks :
    # "address_v4","latitude","longitude" != Null et "status_name"=="Connected"
    #then we can name them with "id" and "country_code" for example

    landmarks = [Landmark(str(p['id'])+str(p['country_code']), p['latitude'], p['longitude'], p['address_v4'],p['id']) for p in probes['objects'] \
                if is_selectable(p)]
    
    return landmarks