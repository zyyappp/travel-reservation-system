import subprocess
import platform

def clear():
    if platform.system() == "Windows":
        subprocess.run("cls", shell=True)
    else:
        subprocess.run("clear", shell=True)

def print_header(title, quantity=60):
        clear()
        print(f"\n{'─'*quantity}\n{title}\n{'─'*quantity}\n")