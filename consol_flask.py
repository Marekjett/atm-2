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
def send_to_server(msg):
    if msg in in_serv:
        in_serv[msg]()
        return f"[LOCAL] Wykonano komendę {msg}"
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
