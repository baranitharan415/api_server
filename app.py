from flask import Flask, request, jsonify
from datetime import datetime
import threading
import time
import requests
import json

app = Flask(__name__)

# In-memory store
received_data = []

@app.route('/api/data', methods=['POST'])
def receive_data():
    if request.is_json:
        data = request.get_json()
        print(data)
        # Current timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        # url = "https://webhook.site/5cb53d43-c818-46ee-b014-77b2e11ffdc7"
        # response = requests.post(url, json=data)
        # print(response)
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
def get_data():
    return jsonify(received_data), 200


# ---- Extra: Auto POST test when server starts ----

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=5000)

