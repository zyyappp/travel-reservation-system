#module name  : cli_helper.py
#date created : 13th August 2026
#created by   :
#imported     : subprocess, platform
#amendment    :
#remark       : clearing CLI & printing UI
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