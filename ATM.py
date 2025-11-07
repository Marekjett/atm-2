import socket
import time

host = "localhost"
port = 9809

with socket.socket(socket.AF_INET,socket.SOCK_STREAM) as s:
    s.connect((host,port))
    msg = "saldo"
    s.sendall(msg.encode())
    data = s.recv(1024)
    print("server odpowiedzial ",data.decode())
    print("pingujemy")
    msg = "ping"
    start = time.time()
    s.sendall(msg.encode())
    stop_data = s.recv(1024)  # to będą bajty
    stop_str = stop_data.decode().strip()  # np. "1730910591.2345"

    try:
        stop_server_time = float(stop_str)
        latency = (stop_server_time - start) * 1000  # ms
        print(f"Ping: {latency:.2f} ms (różnica czasu lokalnego i serwera)")
    except ValueError:
        print("Błąd: serwer nie zwrócił liczby — dostałem:", stop_str)