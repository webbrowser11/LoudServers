from flask import flask, jsonify
from pythonping import ping
import threading

website = input("website to ping:").lower()

app = flask(__name__)
pinging = False

def ping_server():
    global pinging
    while pinging:
        response = ping(website, count=1)
        print(response)

@app.route('/start_ping', methods=['POST'])
def start_ping():
    global pinging
    if not pinging:
        pinging = True
        threading.Thread(target=ping_server).start()
        return jsonify({"status": "Pinging started"}),200
    else:
        return jsonify({"status:" "Pinging started"}),400
    
@app.route('/stop_ping', methods=["POST"])
def stop_ping():
    global pinging 
    pinging = False
    return jsonify({"status": "Pinging stopped"}),200

if __name__ == '__main__':
    app.run(debug=True)
