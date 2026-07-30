"""
Script de compilação automatizada com Nuitka para gerar o .EXE standalone do aplicativo PySide6.
"""

import sys
import os
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent

def build_exe():
    print("==================================================")
    print("INICIANDO COMPILACAO DO COBRANCABOT COM NUITKA")
    print("==================================================")

    cmd = [
        sys.executable,
        "-m", "nuitka",
        "--standalone",
        "--plugin-enable=pyside6",
        "--include-package=src",
        "--include-package=config",
        "--output-dir=dist",
        "--output-filename=CobrancaBot.exe",
        "--windows-console-mode=disable",
        "--assume-yes-for-downloads",
        "--show-progress",
        "app.py"
    ]

    print(f"Executando comando: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(BASE_DIR))

    if result.returncode == 0:
        print("\n==================================================")
        print("COMPILACAO CONCLUIDA COM SUCESSO!")
        print("O arquivo executavel esta disponivel em: dist/CobrancaBot.exe")
        print("==================================================")
    else:
        print(f"\nFalha na compilacao com Nuitka (Codigo de erro: {result.returncode})")

if __name__ == "__main__":
    build_exe()
