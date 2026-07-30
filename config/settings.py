import os
import sys
from pathlib import Path
from dotenv import load_dotenv

if getattr(sys, 'frozen', False):
    APP_DIR = Path(sys.executable).resolve().parent
    BUNDLE_DIR = Path(sys._MEIPASS)
else:
    APP_DIR = Path(__file__).resolve().parent.parent
    BUNDLE_DIR = APP_DIR

# Garantir existência do diretório config local ao lado do executável/projeto
(APP_DIR / "config").mkdir(parents=True, exist_ok=True)

# Carregar arquivo .env (prioriza o .env local da pasta do app, fallback para o embutido)
env_path = APP_DIR / "config" / ".env"
if not env_path.exists():
    bundled_env = BUNDLE_DIR / "config" / ".env"
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
    _cred_app = APP_DIR / "config" / "google_credentials.json"
    if _cred_app.exists():
        GOOGLE_CREDENTIALS_FILE: Path = _cred_app
    else:
        GOOGLE_CREDENTIALS_FILE: Path = BUNDLE_DIR / "config" / "google_credentials.json"

    GSHEET_SPREADSHEET_NAME: str = os.getenv("GSHEET_SPREADSHEET_NAME", "Base_Pendencias")

    APP_DIR: Path = APP_DIR
    BUNDLE_DIR: Path = BUNDLE_DIR
    INPUT_DIR: Path = APP_DIR / "data" / "input"
    OUTPUT_DIR: Path = APP_DIR / "data" / "output"
    
    import tempfile
    TEMP_DIR: Path = Path(tempfile.gettempdir()) / "CobobraBot" / "temp_anexos"

# Garantir existência dos diretórios de dados
Settings.INPUT_DIR.mkdir(parents=True, exist_ok=True)
Settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
Settings.TEMP_DIR.mkdir(parents=True, exist_ok=True)

settings = Settings()
