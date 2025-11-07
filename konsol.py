import socket
import konsol_funcs as f
import configparser
import sys
import aps

print("wczytanie data")

HOST = "localhost"
conf = configparser.ConfigParser()
conf.read("conf.ini")
key = conf["kody"]["key"]
admin = conf["kody"]["admin"]
PORT = int(conf["server"]["port"])
# lokalne komendy klienta
in_serv = {
    "exit": f.func1
}
if not aps.validate_key(int(key)):
    print("key nie przesżło")
    raise ValueError("Key JEST NIE POPRAWNYT PO KLINETA")
def consol(m, sock):

    if m in in_serv:
        # lokalna komenda
        in_serv[m]()
    else:
        # wysyłamy do serwera
        sock.sendall(m.encode())
        data = sock.recv(1024)
        print(f"[SERVER]: {data.decode()}")

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as k:
    k.connect((HOST, PORT))
    print(f"[KLIENT] Połączono z serwerem {HOST}:{PORT}")
    k.sendall("admin".encode())

    data= k.recv(1024)
    print(f"dostep to {data.decode()}")
    k.sendall(admin.encode())
    print("wysłano prosbe o dostep")

    data = k.recv(1024)
    if data.decode() == "pass":
        k.sendall(key.encode())
        data = k.recv(1024)
        if data.decode() == "ok":
            print("jest dostep")
            while True:
                msg = input("> ").strip()
                if msg == "":
                    continue
                if msg == "exit":
                    print("[konsola] Rozłączanie...")
                    break
                consol(msg, k)
        else:
            print("nie udało sie 2")
    else:
        print("nie udalo 1")