from flask import Flask, jsonify, request
from pythonping import ping
import threading

app = Flask(__name__)
pinging = False
website = None

def ping_server():
    global pinging
    while pinging:
        response = ping(website, count=1)
        print(response)

@app.route('/start_ping', methods=['POST'])
def start_ping():
    global pinging, website
    data = request.json
    website = data.get('website', '').lower()
    
    if not pinging and website:
        pinging = True
        threading.Thread(target=ping_server).start()
        return jsonify({"status": "Pinging started for " + website}), 200
    else:
        return jsonify({"status": "Pinging already started or no website provided"}), 400

@app.route('/stop_ping', methods=["POST"])
def stop_ping():
    global pinging 
    pinging = False
    return jsonify({"status": "Pinging stopped"}), 200

if __name__ == '__main__':
    app.run(debug=True)
