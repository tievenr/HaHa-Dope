import os
import requests
import json

namenode_url = "http://127.0.0.1:9870"

def namenode_healthcheck():

    try: 
        res = requests.get(namenode_url +"/health")
        return res.status_code == 200
    
    except: 
        return False
    
if __name__ == "__main__":
    print("Testing NameNode connection...")
    if namenode_healthcheck():
        print("NameNode is healthy!")
    else:
        print("NameNode is not reachable")
