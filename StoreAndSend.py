from xmlrpc.client import ProtocolError
from flask import Flask, request, jsonify,after_this_request
from datetime import datetime
import paho.mqtt.client as mqtt
import os
import logging
import threading
import time
import requests
import json

app = Flask(__name__)
folder_path = r"D:\t"

# In-memory store
received_data = []
file_count = 0

url = ""
val = ""

broker = "192.168.1.122"
port = 1883
topic = "details"
thread_enable = True


def on_connect(client, userdata,  flags,rc):
    if rc == 0:
        print("✅ Connected to broker")
    else:
        print("❌ Connection failed")

def on_publish(client, userdata, mid):
    print(f"📩 Message {mid} successfully published!")

def on_message(client, userdata, msg):
    global val
    val = msg.payload.decode()



def register(data):
    global val
    dict_set = {i: False for i in range(1, 3)}
    while True:
        for i in range(2):
            if dict_set[i+1]:
                continue
            global topic
            topic = f"details{i+1}"
            client = mqtt.Client()
            client.username_pw_set("bharani","1234")
            client.connect(broker,port,60)
            client.on_connect = on_connect
            client.on_publish = on_publish
            client.on_message = on_message

            client.loop_start()
            client.subscribe(f"success{i+1}")
            result = client.publish(topic,json.dumps(data))

            status = result[0]
            if status == 0:
                print(f"✅ Message published successfully to topic {topic}")
            else:
                print(f"❌ Failed to publish message to topic {topic}")
            print("Published",json.dumps(data))
            start = time.time()
            while time.time() - start < 5:
                if(val ==str(i+1)):
                    dict_set[i+1] = True
                    print("Value Setted",str(i+1))
                    val = ""
                    break
        if all(dict_set.values()):
            print("exit")
            break


@app.route('/api/NewRegister', methods=['POST'])
def register_thread():
    data = request.get_json()
    if any(value in [None, ""] for value in data.values()):
        return jsonify({"status": "Failed", "message": "Value is Wrong"}), 500
    if not data:
        return jsonify({"status": "Failed", "message": "Its Not Json Format"}), 500
    threading.Thread(target=register, args=(data,),daemon=True).start()
    return jsonify({"status": "success", "message": "Data received"}), 200



def fail_post(file_path):
    global url,thread_enable
    files = os.listdir(file_path)
    for i in files:
        full_path = os.path.join(file_path,i)
        if os.path.isfile(full_path):
            if full_path.endswith(".json"):
                # print(full_path)
                with open(full_path,"r") as json_file:
                    try:
                        data = json.load(json_file) 
                    except json.JSONDecodeError as e:
                        logging.warning(e)
                        os.remove(full_path)
                        continue
                    except Exception as e:
                        logging.warning(e)
                        continue
                response = send(data)
                if response in (200,201):
                    try:
                        os.remove(full_path)
                        continue
                    except Exception as e:
                        logging.warning(e)
                else:
                    thread_enable = True
                    return
        else: 
            if i == "Employee" :
                url = "http://localhost:8080/Employee"
            if i == "Loom":
                url = "http://localhost:8080/loom"
            fail_post(full_path)
            if os.path.exists(full_path) and len(os.listdir(full_path)) == 0:
                os.rmdir(full_path)
    if not os.listdir(folder_path): 
        thread_enable = True
    return


def send(data):
    try:
        # url = "https://webhook.site/00420d0e-970f-4cf5-8e57-d7a02eba56b5"
        response = requests.post(url, json=data)
        return response.status_code
    except requests.exceptions.ConnectionError as e:
        logging.warning(e)
        return -200
    
    
    
def store_data(data):
    global url
    store_folder_path = r"D:\t" + "\\store_data"
    os.makedirs(store_folder_path,exist_ok=True)
    if(request.path == '/api/Employee'):
        store_folder_path = store_folder_path + "\\Employee"
        os.makedirs(store_folder_path,exist_ok=True)
        url = "http://localhost:8080/Employee"
    if(request.path == '/api/data'):
        store_folder_path = store_folder_path + "\\Loom"
        os.makedirs(store_folder_path,exist_ok=True)
        url = "http://localhost:8080/loom"
    store_file_path = store_folder_path +"\\" + str(data.get("machineId"))
    os.makedirs(store_file_path,exist_ok=True)
    store_file_date = store_file_path +"\\"+datetime.now().strftime("%Y-%m-%d")
    os.makedirs(store_file_date,exist_ok=True)
    store_file_name = store_file_date+"\\"+datetime.now().strftime("%H-%M-%S")+".json"
    with open(store_file_name,"w") as file:
        json.dump(data,file,indent=4)
    # file_name  = os.path.join(folder_path,str(5),str(datetime.now().strftime("%H-%M-%S"))+".json")


def fail_data(data):
    fail_folder_path = r"D:\t" + "\\fail_data"
    os.makedirs(fail_folder_path,exist_ok=True)
    if(request.path == '/api/Employee'):
        fail_folder_path = fail_folder_path + "\\Employee"
        os.makedirs(fail_folder_path,exist_ok=True)
    if(request.path == '/api/data'):
        fail_folder_path = fail_folder_path + "\\Loom"
        os.makedirs(fail_folder_path,exist_ok=True)
    fail_file_path = fail_folder_path +"\\" + str(data.get("machineId"))
    os.makedirs(fail_file_path,exist_ok=True)
    fail_file_date = fail_file_path +"\\"+datetime.now().strftime("%Y-%m-%d")
    os.makedirs(fail_file_date,exist_ok=True)
    fail_file_name = fail_file_date+"\\"+datetime.now().strftime("%H-%M-%S")+".json"
    with open(fail_file_name,"w") as file:
        json.dump(data,file,indent=4)




@app.route('/api/data', methods=['POST'])
@app.route('/api/Employee', methods=['POST'])


def receive_data():
    logging.basicConfig(level=logging.INFO , filename=r"C:\Users\advan\OneDrive\Documents\PlatformIO\python\Projects\logging\log.txt",filemode="w")

    if request.is_json:
        data = request.get_json()
        if not data:
            return jsonify({"status": "Failed", "message": "Its Not Json Format"}), 500
        if any(value in [None, ""] for value in data.values()):
            return jsonify({"status": "Failed", "message": "Value is Wrong"}), 500
        # Current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        store_data(data)
        if send(data) not in (200,201):
            fail_data(data)
        else:
            global thread_enable
            if thread_enable:
                temp  = folder_path+"\\fail_data"
                threading.Thread(target=fail_post,args=(temp,),daemon=True).start()
                thread_enable = False
        # Print received data
        print("\n" + "="*50)
        print(f"Received data from client at {timestamp}:")
        print("-"*50)
        for key, value in data.items():
            print(f"{key:>15}: {value}")
        print("="*50 + "\n")

        # Save to memory
        received_data.append(data)
      
        return jsonify({"status": "success", "message": "Data received"}), 200
    else:
        print("\n" + "!"*50)
        print("ERROR: Received non-JSON data")
        print("!"*50 + "\n")
        return jsonify({"status": "error", "message": "Request must be JSON"}), 400



@app.route('/api/data', methods=['GET'])
@app.route('/api/NewRegister', methods=['GET'])
@app.route('/api/Employee', methods=['GET'])
def get_data():
    return jsonify(received_data), 200


# ---- Extra: Auto POST test when server starts ----

if __name__ == '__main__':
    # threading.Thread(target=register_thread,daemon=True).start()
    
    app.run(host='0.0.0.0', port=8000, debug=True)