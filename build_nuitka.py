"""
Script de compilação automatizada com Nuitka para gerar o .EXE standalone do aplicativo PySide6.
"""

import sys
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def build_exe():
    print("==================================================")
    print("🚀 INICIANDO COMPILAÇÃO DO COBRANÇABOT COM NUITKA")
    print("==================================================")

    cmd = [
        sys.executable,
        "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--plugin-enable=pyside6",
        "--include-package=src",
        "--include-package=config",
        "--include-data-dir=config=config",
        "--output-dir=dist",
        "--output-filename=CobrancaBot.exe",
        "--windows-console-mode=disable",
        "--assume-yes-for-downloads",
        "app.py"
    ]

    print(f"Executando comando: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=str(BASE_DIR))

    if result.returncode == 0:
        print("\n==================================================")
        print("✅ COMPILAÇÃO CONCLUÍDA COM SUCESSO!")
        print("O arquivo executável está disponível em: dist/CobrancaBot.exe")
        print("==================================================")
    else:
        print(f"\n❌ Falha na compilação com Nuitka (Código de erro: {result.returncode})")

if __name__ == "__main__":
    build_exe()
