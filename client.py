import os
import requests

namenode_url = "http://127.0.0.1:9870"

def namenode_healthcheck():

    try: 
        res = requests.get(namenode_url +"/health")
        return res.status_code == 200
    
    except: 
        return False


def upload(filename):
    url = namenode_url + "/files"
    payload = {
        "filename": filename,
        "filesize_bytes": os.path.getsize(filename)  
    }
    try:
        r = requests.post(url, json=payload)
        return r  
    except Exception as e:
        print(f"Upload error: {e}")
        return None

if __name__ == "__main__":
    print("Testing NameNode connection...")
    if namenode_healthcheck():
        print("NameNode is healthy!")
        
        filename = os.path.join("client_testfiles", "test.txt")
        print(f"Uploading {filename}...")
        response = upload(filename)
        
        if response:
            print(f"Response status: {response.status_code}")
            print(f"Response: {response.text}")
        else:
            print("Upload failed")
    else:
        print("NameNode is not reachable")