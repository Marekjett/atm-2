import socket
import time
import configparser
import sys
import random
import aps

conf = configparser.ConfigParser()
conf.read("conf.ini")
port = int(conf["server"]["port"])
host = "localhost"
key = conf["kody"]["key"]
admin = conf["kody"]["admin"]
args = sys.argv
run = True

# --- Funkcje serwera ---
def func1():
    print("func1")
    return 5000

def func2():
    print("func2z")
    return time.time()

def decrypt(msg):
    return "zdeszfrowano " + msg



skrypty = {
    "saldo": func1,
    "ping": func2,
    "decrypt": decrypt,
    "t": aps.validate_key,
    "gen": aps.gen_key
}

# --- Serwer ---
def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  #
        s.bind((host, port))
        s.listen()

        print(f"[SERVER] Startuje na {host}:{port}")

        while run:
            conn, addr = s.accept()
            print("Połączono z", addr)
            with conn:
                # --- Logowanie admina ---
                data = conn.recv(1024)
                if not data:
                    continue
                msg = data.decode().strip()

                if msg == "admin":
                    conn.sendall("podaj admin i pin".encode())

                    data = conn.recv(1024)
                    if data.decode().strip() == admin:
                        conn.sendall("pass".encode())

                        data = conn.recv(1024)
                        if data.decode().strip() == key:
                            conn.sendall("ok".encode())
                            print("Witaj adminie!")

                            # --- Tryb komend admina ---
                            while True:
                                data = conn.recv(1024)
                                if not data:
                                    print("Admin się rozłączył.")
                                    break

                                msg = data.decode().strip()
                                if msg.lower() == "exit":
                                    print("Admin zakończył sesję.")
                                    break

                                # rozbij najpierw po ":", jeśli nie ma – spróbuj po spacji
                                if ":" in msg:
                                    parts = msg.split(":", 1)
                                elif " " in msg:
                                    parts = msg.split(" ", 1)
                                else:
                                    parts = [msg]

                                cmd = parts[0].strip()
                                arg = parts[1].strip() if len(parts) > 1 else None

                                if cmd in skrypty:
                                    try:
                                        if arg is not None:
                                            send = skrypty[cmd](arg)
                                        else:
                                            send = skrypty[cmd]()
                                        conn.sendall(str(send).encode())
                                    except Exception as e:
                                        conn.sendall(f"Błąd wykonania: {e}".encode())
                                else:
                                    conn.sendall(f"Brak komendy kotku {msg}".encode())
                        else:
                            conn.sendall("fail".encode())
                            conn.close()
                    else:
                        conn.sendall("fail".encode())
                        conn.close()
                else:
                    conn.sendall("Niepoprawny użytkownik".encode())
                    conn.close()

# --- Dodatkowe funkcje CLI ---
def main_arg():
    global args
    if len(args) > 1 and args[1] == "gen":
        x = aps.gen_key()
        print(x)
    elif len(args) > 2 and args[1] == "gen" and args[2] == "-s":
        pass

if __name__ == "__main__":
    if len(args) > 1:
        main_arg()
    else:
        main()
