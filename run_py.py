#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import signal
import time
import argparse
from pathlib import Path
from datetime import datetime

# plik z zapisanymi procesami
DATA_FILE = Path.home() / ".run_py_processes.json"


# wczytaj dane
def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"⚠️  Błąd odczytu pliku danych: {e}")
            return {}
    return {}


# zapisz dane
def save_data(data):
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError as e:
        print(f"❌ Błąd zapisu pliku danych: {e}")


def start(script, args=None):
    """Uruchom skrypt Python w tle"""
    if not Path(script).exists():
        print(f"❌ Plik {script} nie istnieje!")
        return False

    data = load_data()

    # Sprawdź czy skrypt już działa
    if script in data:
        pid = data[script]["pid"]
        if Path(f"/proc/{pid}").exists():
            print(f"⚠️  Skrypt {script} już działa (PID {pid})")
            return False
        else:
            # Usuń martwy proces
            del data[script]

    # Przygotuj komendę
    cmd = ["python3", script]
    if args:
        cmd.extend(args)

    # Uruchom proces
    try:
        proc = subprocess.Popen(cmd)
        data[script] = {
            "pid": proc.pid,
            "start_time": datetime.now().isoformat(),
            "command": " ".join(cmd),
            "status": "running"
        }
        save_data(data)
        print(f"✅ Uruchomiono {script} (PID {proc.pid})")
        return True
    except Exception as e:
        print(f"❌ Błąd uruchamiania {script}: {e}")
        return False


def list_processes(verbose=False):
    """Wyświetl listę procesów"""
    data = load_data()
    if not data:
        print("📭 Brak uruchomionych skryptów.")
        return

    print(f"🔹 Aktywne procesy ({len(data)}):")
    for name, info in data.items():
        pid = info["pid"]
        start_time = info.get("start_time", "nieznany")

        # Sprawdź czy proces działa
        if Path(f"/proc/{pid}").exists():
            status = "🟢 działa"
            # Pobierz czas uruchomienia procesu
            try:
                proc_start = Path(f"/proc/{pid}").stat().st_ctime
                uptime = time.time() - proc_start
                uptime_str = f"{int(uptime // 3600)}h {int((uptime % 3600) // 60)}m"
            except:
                uptime_str = "nieznany"
        else:
            status = "🔴 nie działa"
            uptime_str = "zakończony"

        print(f"  📁 {name:30}")
        print(f"     PID: {pid:6} — {status}")
        print(f"     Uruchomiony: {start_time}")
        print(f"     Czas pracy: {uptime_str}")

        if verbose:
            print(f"     Komenda: {info.get('command', 'nieznana')}")
        print()


def stop(script, force=False):
    """Zatrzymaj skrypt"""
    data = load_data()
    if script not in data:
        print(f"❌ Nie znaleziono procesu dla {script}")
        return False

    pid = data[script]["pid"]
    script_name = script

    try:
        if force:
            os.kill(pid, signal.SIGKILL)
            print(f"🛑 Wymuszone zatrzymanie {script_name} (PID {pid})")
        else:
            os.kill(pid, signal.SIGTERM)
            print(f"🛑 Zatrzymano {script_name} (PID {pid})")

        # Poczekaj chwilę i sprawdź czy proces zakończony
        time.sleep(0.5)
        if not Path(f"/proc/{pid}").exists():
            del data[script_name]
            save_data(data)
            return True
        else:
            print(f"⚠️  Proces {pid} nie zakończył się, użyj --force")
            return False

    except ProcessLookupError:
        print(f"⚠️  Proces {pid} już nie działa.")
        del data[script_name]
        save_data(data)
        return True
    except PermissionError:
        print(f"❌ Brak uprawnień do zatrzymania procesu {pid}")
        return False
    except Exception as e:
        print(f"❌ Błąd zatrzymywania procesu: {e}")
        return False


def stop_all(force=False):
    """Zatrzymaj wszystkie skrypty"""
    data = load_data()
    if not data:
        print("📭 Brak procesów do zatrzymania.")
        return

    print(f"🛑 Zatrzymywanie {len(data)} procesów...")
    success_count = 0

    # Zatrzymaj w odwrotnej kolejności (może pomóc w zależnościach)
    for script in reversed(list(data.keys())):
        if stop(script, force):
            success_count += 1

    print(f"✅ Zatrzymano {success_count}/{len(data)} procesów")


def restart(script, args=None):
    """Restartuj skrypt"""
    print(f"🔄 Restartowanie {script}...")
    if stop(script):
        time.sleep(1)  # Chwila przerwy
        start(script, args)


def status(script):
    """Sprawdź status konkretnego skryptu"""
    data = load_data()
    if script not in data:
        print(f"❌ Skrypt {script} nie jest uruchomiony")
        return

    info = data[script]
    pid = info["pid"]

    if Path(f"/proc/{pid}").exists():
        print(f"🟢 {script} - DZIAŁA (PID {pid})")
        print(f"   Uruchomiony: {info.get('start_time', 'nieznany')}")
        print(f"   Komenda: {info.get('command', 'nieznana')}")

        # Informacje o procesie
        try:
            with open(f"/proc/{pid}/stat", "r") as f:
                stat_data = f.read().split()
                cpu_time = int(stat_data[13]) + int(stat_data[14])  # utime + stime
                print(f"   Czas CPU: {cpu_time} ticks")
        except:
            pass
    else:
        print(f"🔴 {script} - NIE DZIAŁA (PID {pid})")
        # Usuń martwy proces
        del data[script]
        save_data(data)


def cleanup():
    """Wyczyść martwe procesy z danych"""
    data = load_data()
    removed_count = 0

    for script, info in list(data.items()):
        pid = info["pid"]
        if not Path(f"/proc/{pid}").exists():
            del data[script]
            removed_count += 1
            print(f"🧹 Usunięto martwy proces: {script} (PID {pid})")

    if removed_count > 0:
        save_data(data)
        print(f"✅ Usunięto {removed_count} martwych procesów")
    else:
        print("✅ Brak martwych procesów do usunięcia")


def main():
    parser = argparse.ArgumentParser(
        description="Menadżer skryptów Python - uruchamiaj i zarządzaj skryptami w tle",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Przykłady użycia:
  run_py start skrypt.py          # Uruchom skrypt
  run_py start skrypt.py arg1     # Uruchom z argumentami
  run_py stop skrypt.py           # Zatrzymaj skrypt
  run_py stop --all               # Zatrzymaj wszystkie
  run_py restart skrypt.py        # Restartuj skrypt
  run_py list                     # Lista procesów
  run_py list --verbose           # Szczegółowa lista
  run_py status skrypt.py         # Status skryptu
  run_py cleanup                  # Wyczyść martwe procesy
        """
    )

    parser.add_argument("command", nargs="?", help="Polecenie (start, stop, list, restart, status, cleanup)")
    parser.add_argument("target", nargs="?", help="Plik skryptu lub '--all'")
    parser.add_argument("args", nargs=argparse.REMAINDER, help="Argumenty dla skryptu")

    parser.add_argument("--force", action="store_true", help="Wymuszone zatrzymanie")
    parser.add_argument("--verbose", "-v", action="store_true", help="Szczegółowe wyjście")
    parser.add_argument("--all", action="store_true", help="Wszystkie procesy")

    # Dla kompatybilności wstecznej
    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    # Obsługa starych poleceń dla kompatybilności
    if len(sys.argv) >= 2 and sys.argv[1].endswith('.py'):
        start(sys.argv[1], sys.argv[2:])
        return

    # Nowe polecenia
    if args.command == "start" or (len(sys.argv) == 2 and sys.argv[1].endswith('.py')):
        script = args.target or (sys.argv[1] if len(sys.argv) == 2 else None)
        if script:
            start(script, args.args)
        else:
            print("❌ Podaj nazwę skryptu do uruchomienia")

    elif args.command == "stop":
        if args.all or args.target == "--all":
            stop_all(args.force)
        elif args.target:
            stop(args.target, args.force)
        else:
            print("❌ Podaj nazwę skryptu lub użyj --all")

    elif args.command == "restart":
        if args.target:
            restart(args.target, args.args)
        else:
            print("❌ Podaj nazwę skryptu do restartowania")

    elif args.command == "list":
        list_processes(args.verbose)

    elif args.command == "status":
        if args.target:
            status(args.target)
        else:
            print("❌ Podaj nazwę skryptu")

    elif args.command == "cleanup":
        cleanup()

    else:
        parser.print_help()


if __name__ == "__main__":
    main()