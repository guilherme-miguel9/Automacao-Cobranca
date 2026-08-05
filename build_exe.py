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

    venv_python = BASE_DIR / ".venv" / "Scripts" / "python.exe"
    python_bin = str(venv_python) if venv_python.exists() else sys.executable
    print(f"Utilizando Python: {python_bin}")

    spec_file = BASE_DIR / "CobobraBot.spec"
    if spec_file.exists():
        cmd = [python_bin, "-m", "PyInstaller", "--clean", "--noconfirm", "CobobraBot.spec"]
    else:
        cmd = [
            python_bin,
            "-m", "PyInstaller",
            "--onefile",
            "--noconsole",
            "--clean",
            "--name=CobobraBot",
            "--add-data=config;config",
            "--add-data=src/assets;src/assets",
            "--add-data=gateway;gateway",
            "--add-binary=C:/Program Files/nodejs/node.exe;.",
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
