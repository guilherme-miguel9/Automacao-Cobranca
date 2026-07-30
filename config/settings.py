import os
import sys
from pathlib import Path
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent

# Garantir existência do diretório config local ao lado do executável/projeto
(BASE_DIR / "config").mkdir(parents=True, exist_ok=True)

# Carregar arquivo .env (prioriza o .env local da pasta do app, fallback para o embutido)
env_path = BASE_DIR / "config" / ".env"
if not env_path.exists() and getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
    bundled_env = Path(sys._MEIPASS) / "config" / ".env"
    if bundled_env.exists():
        env_path = bundled_env

if env_path.exists():
    load_dotenv(env_path, override=True)

class Settings:
    # Modo Simulação (Dry Run)
    DRY_RUN: bool = os.getenv("DRY_RUN", "True").lower() in ("true", "1", "yes")

    # Configurações de E-mail
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", 587))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "Robô de Cobrança")

    # WhatsApp / OpenClaw Integration
    WHATSAPP_API_URL: str = os.getenv("WHATSAPP_API_URL", "http://localhost:8000/api/v1/send-message")
    WHATSAPP_API_TOKEN: str = os.getenv("WHATSAPP_API_TOKEN", "")

    # Google Sheets
    GOOGLE_CREDENTIALS_FILE: Path = BASE_DIR / os.getenv("GOOGLE_CREDENTIALS_FILE", "config/google_credentials.json")
    GSHEET_SPREADSHEET_NAME: str = os.getenv("GSHEET_SPREADSHEET_NAME", "Base_Pendencias")

    BASE_DIR: Path = BASE_DIR
    INPUT_DIR: Path = BASE_DIR / "data" / "input"
    OUTPUT_DIR: Path = BASE_DIR / "data" / "output"
    TEMP_DIR: Path = BASE_DIR / "data" / "temp_anexos"

# Garantir existência dos diretórios de dados
Settings.INPUT_DIR.mkdir(parents=True, exist_ok=True)
Settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
Settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
