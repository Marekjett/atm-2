from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
import socket
import configparser
import aps
import konsol_funcs as f

# Flask setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

# Config
conf = configparser.ConfigParser()
conf.read("conf.ini")
HOST = "localhost"
PORT = int(conf["server"]["port"])
key = conf["kody"]["key"]
admin = conf["kody"]["admin"]

# Lokalne komendy
in_serv = {
    "exit": f.func1
}

# Połączenie TCP z serwerem
tcp_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_sock.connect((HOST, PORT))
tcp_sock.sendall("admin".encode())
data = tcp_sock.recv(1024)
tcp_sock.sendall(admin.encode())
data = tcp_sock.recv(1024)
if data.decode() == "pass":
    tcp_sock.sendall(key.encode())
    data = tcp_sock.recv(1024)
    if data.decode() != "ok":
        raise ValueError("Nie udało się połączyć z serwerem")
else:
    raise ValueError("Nie udało się połączyć z serwerem")

# Funkcja wysyłania wiadomości do serwera TCP
import time  # dodaj na początku pliku


# Funkcja wysyłania wiadomości do serwera TCP
def send_to_server(msg):
    if msg in in_serv:
        in_serv[msg]()
        return f"[LOCAL] Wykonano komendę {msg}"

    if msg.lower() == "ping":
        start_time = time.time()
        tcp_sock.sendall(msg.encode())
        data = tcp_sock.recv(1024)
        end_time = time.time()
        try:
            server_time = float(data.decode())
            ping_ms = (end_time - start_time) * 1000  # ping w ms
            return f"[PING] {ping_ms:.2f} ms"
        except ValueError:
            return f"[ERROR] Nieprawidłowa odpowiedź serwera: {data.decode()}"

    tcp_sock.sendall(msg.encode())
    data = tcp_sock.recv(1024)
    return f"[SERVER]: {data.decode()}"


# Strona główna
@app.route("/")
def index():
    return render_template("index.html")

# Socket do komunikacji z frontendem
@socketio.on("send_message")
def handle_message(msg):
    response = send_to_server(msg)
    emit("receive_message", response)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, allow_unsafe_werkzeug=True)
