import socket
import konsol_funcs as f
import configparser
import aps
import sys

# --- Konfiguracja ---
HOST = "localhost"

conf = configparser.ConfigParser()
conf.read("conf.ini")
PORT = int(conf["server"]["port"])

# Odczytanie i przygotowanie danych logowania
admin_config = conf["kody"]["admin"].strip()
key_str = conf["kody"]["key"].strip()

try:
    key_int = int(key_str)
except ValueError:
    print("[ERROR] Klucz w pliku conf.ini nie jest liczbą!")
    sys.exit(1)

# --- Wstępna walidacja klucza ---
if not aps.validate_key(key_int):
    print("[ERROR] Klucz niepoprawny. Nie można połączyć się z serwerem.")
    sys.exit(1)

# --- Lokalne komendy klienta ---
in_serv = {
    "exit": f.func1
}

# --- Funkcja wysyłania wiadomości ---
def consol(msg, sock):
    if msg in in_serv:
        in_serv[msg]()
    else:
        sock.sendall(msg.encode())
        data = sock.recv(1024)
        print(f"[SERVER]: {data.decode()}")

# --- Główna część klienta ---
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as k:
    try:
        k.connect((HOST, PORT))
        print(f"[KLIENT] Połączono z serwerem {HOST}:{PORT}")
    except Exception as e:
        print(f"[ERROR] Nie udało się połączyć z serwerem: {e}")
        sys.exit(1)

    # --- Krok 1: login ---
    while True:
        login_input = input("Podaj login: ").strip()
        if login_input == "":
            continue
        k.sendall(login_input.encode())
        data = k.recv(1024)
        if data.decode() == "pass":
            break
        print("Niepoprawny login, spróbuj ponownie")

    # --- Krok 2: hasło ---
    while True:
        password_input = input("Podaj hasło: ").strip()
        if password_input == "":
            continue
        k.sendall(password_input.encode())
        data = k.recv(1024)
        if data.decode() == "pass":
            print("[INFO] Hasło poprawne!")
            break
        print("Niepoprawne hasło, spróbuj ponownie")

    # --- Krok 3: wysyłamy klucz automatycznie ---
    k.sendall(str(key_int).encode())
    data = k.recv(1024)
    if data.decode() != "ok":
        print("[ERROR] Serwer odrzucił klucz. Kończę działanie.")
        sys.exit(1)
    print("[INFO] Logowanie zakończone pomyślnie! Możesz wysyłać komendy.")

    # --- Pętla konsoli ---
    while True:
        msg = input("> ").strip()
        if msg == "":
            continue
        if msg == "exit":
            print("[konsola] Rozłączanie...")
            break
        consol(msg, k)
