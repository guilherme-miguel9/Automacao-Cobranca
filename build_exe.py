"""
Script de compilação automatizada com PyInstaller para gerar o .EXE standalone do aplicativo PySide6.
"""

import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def build_exe():
    print("==================================================")
    print("INICIANDO COMPILACAO DO COBOBRABOT COM PYINSTALLER")
    print("==================================================")

    cmd = [
        sys.executable,
        "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--clean",
        "--name=CobobraBot",
        "--add-data=config;config",
        "--add-data=src/assets;src/assets",
        "--icon=src/assets/icon.ico",
        "app.py"
    ]

    print(f"Executando comando: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(BASE_DIR))

    if result.returncode == 0:
        print("\n==================================================")
        print("COMPILACAO CONCLUIDA COM SUCESSO!")
        print("O arquivo executavel esta disponivel em: dist/CobobraBot.exe")
        print("==================================================")
    else:
        print(f"\nFalha na compilacao com PyInstaller (Codigo de erro: {result.returncode})")

if __name__ == "__main__":
    build_exe()
