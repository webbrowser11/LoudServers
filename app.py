from flask import Flask, jsonify, request
from pythonping import ping
import threading
import time

app = Flask(__name__)
pinging = False
website = None
ping_results = []

def ping_server():
    global pinging, ping_results
    while pinging:
        response = ping(website, count=1)
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
        <title>Loud Servers</title>
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
        <form id="startPingForm">
            <input type="text" id="website" placeholder="Enter website URL" required>
            <button type="submit">Start Ping</button>
        </form>
        
        <form id="stopPingForm">
            <button type="submit">Stop Ping</button>
        </form>

        <div id="response"></div>

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
        </script>
        <center>copyright © 2024 LoudServers Team</center>
    </body>
    </html>
    '''

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

@app.route('/ping_results', methods=['GET'])
def get_ping_results():
    return jsonify({"results": ping_results})

if __name__ == '__main__':
    app.run(debug=True)
