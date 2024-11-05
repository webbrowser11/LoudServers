from flask import Flask, jsonify, request
from pythonping import ping
import threading
import time
import socket

app = Flask(__name__)
pinging = False
website = None
ping_results = []
ping_ip = None  # To store the IP address of the pinged website

def resolve_ip(hostname):
    try:
        return socket.gethostbyname(hostname)
    except socket.gaierror:
        return None

def ping_server():
    global pinging, ping_results, ping_ip
    ping_ip = resolve_ip(website)  # Resolve the IP address at the start
    
    while pinging and ping_ip:
        response = ping(ping_ip, count=1)
        if response:
            ping_results.append(str(response))
            print(response)
        time.sleep(1)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>LoudServers</title>
        <style>
            body {
                font-family: 'Arial', sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 20px;
            }
            h1 {
                color: #333;
            }
            form {
                margin: 10px 0;
                padding: 10px;
                background-color: #fff;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            input[type="text"] {
                padding: 10px;
                width: calc(100% - 22px);
                margin-bottom: 10px;
                border: 1px solid #ccc;
                border-radius: 4px;
                font-size: 16px;
            }
            button {
                padding: 10px 15px;
                background-color: #007BFF;
                color: #fff;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #0056b3;
            }
            #response {
                margin-top: 20px;
                font-size: 18px;
                color: #333;
            }
        </style>
    </head>
    <body>
        <h1>LoudServers</h1>
        <p>if the websites ip adress not resolved after first hit this means it may not have started the ping hit ping again to verify start if so.</p>
        <form id="startPingForm">
            <input type="text" id="website" placeholder="Enter website URL" required>
            <button type="submit">Start Ping</button>
        </form>
        
        <form id="stopPingForm">
            <button type="submit">Stop Ping</button>
        </form>

        <div id="response"></div>
        <div id="ip"></div>

        <script>
            document.getElementById('startPingForm').addEventListener('submit', function(event) {
                event.preventDefault();
                const website = document.getElementById('website').value;

                fetch('/start_ping', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ website: website }),
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('response').innerText = data.status;
                    updatePingResults();
                });
            });

            document.getElementById('stopPingForm').addEventListener('submit', function(event) {
                event.preventDefault();

                fetch('/stop_ping', {
                    method: 'POST',
                })
                .then(response => response.json())
                .then(data => {
                    document.getElementById('response').innerText = data.status;
                });
            });

            function updatePingResults() {
                fetch('/ping_results')
                .then(response => response.json())
                .then(data => {
                    if (data.ip) {
                        document.getElementById('ip').innerText = "IP Address: " + data.ip;
                    }
                });
            }
        </script>
        <center>copyright © 2024 LoudServers Team</center>
        <center><a href="https://github.com/webbrowser11/LoudServers/edit/main/app.py" style="font-size: 0.8em;">Github</a></center>
    </body>
    </html>
    '''

@app.route('/start_ping', methods=['POST'])
def start_ping():
    global pinging, website, ping_results
    data = request.json
    website = data.get('website', '').lower()
    
    ping_results = []  # Clear previous ping results on new request

    if not pinging and website:
        pinging = True
        threading.Thread(target=ping_server).start()
        return jsonify({"status": f"Pinging started for {website}"}), 200
    else:
        return jsonify({"status": "Pinging already started or no website provided"}), 400

@app.route('/stop_ping', methods=["POST"])
def stop_ping():
    global pinging 
    pinging = False
    return jsonify({"status": "Pinging stopped"}), 200

@app.route('/ping_results', methods=['GET'])
def get_ping_results():
    return jsonify({"results": ping_results, "ip": ping_ip})  # Include IP address in response

if __name__ == '__main__':
    app.run(debug=True)
