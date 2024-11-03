from flask import Flask, jsonify, request
from pythonping import ping
import threading
import time

app = Flask(__name__)
pinging = False
website = None
ping_results = []  # List to hold the ping results

def ping_server():
    global pinging, ping_results
    while pinging:
        response = ping(website, count=1)
        ping_results.append(str(response))  # Store response as a string
        print(response)
        time.sleep(1)  # Optional: Delay between pings

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Ping Service</title>
    </head>
    <body>
        <h1>Ping Service</h1>
        <form id="startPingForm">
            <input type="text" id="website" placeholder="Enter website URL" required>
            <button type="submit">Start Ping</button>
        </form>
        
        <form id="stopPingForm">
            <button type="submit">Stop Ping</button>
        </form>

        <div id="response"></div>
        <h2>Ping Results:</h2>
        <div id="pingResults"></div>  <!-- Area to display ping results -->

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
                    fetchPingResults();  // Start fetching ping results
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

            function fetchPingResults() {
                setInterval(function() {
                    fetch('/ping_results')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('pingResults').innerText = data.results.join('\\n');  // Display results
                    });
                }, 1000); // Fetch results every second
            }
        </script>
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
    return jsonify({"results": ping_results})  # Return the list of ping results

if __name__ == '__main__':
    app.run(debug=True)
