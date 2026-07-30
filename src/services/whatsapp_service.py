import os
import re
import requests
from pathlib import Path
from src.models.pendencia import Pendencia
from src.utils.formatters import formatar_mensagem_pendencia
from src.utils.logger import logger
from config.settings import settings

def baixar_anexo_drive(url_ou_id: str) -> str:
    """
    Baixa o arquivo do Google Drive usando a URL de download direto ou API.
    """
    if not url_ou_id:
        return ""
    
    url_str = str(url_ou_id).strip()
    
    # Se não for URL do Google, repassa direto
    if "drive.google.com" not in url_str and "docs.google.com" not in url_str:
        return url_str

    import re
    drive_match = re.search(r"(?:id=)([\w-]+)", url_str)
    if not drive_match:
        drive_match = re.search(r"/d/([\w-]+)", url_str)
    
    file_id = drive_match.group(1) if drive_match else "unknown"
    
    temp_dir = settings.TEMP_DIR
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    # Detecta a extensão esperada pelo formato da URL
    ext = ".pdf"
    if "ext=xlsx" in url_str or "format=xlsx" in url_str:
        ext = ".xlsx"
    elif "ext=docx" in url_str or "format=docx" in url_str:
        ext = ".docx"
        
    local_filepath = temp_dir / f"anexo_{file_id}{ext}"

    # Se o arquivo local já existe, verificar se é um arquivo de mídia válido (não HTML)
    if local_filepath.exists():
        try:
            with open(local_filepath, "rb") as f:
                head = f.read(512)
                if b"<!DOCTYPE" not in head and b"<html" not in head and len(head) > 50:
                    return str(local_filepath.resolve())
            os.remove(local_filepath)
        except Exception:
            pass

    creds_path = settings.GOOGLE_CREDENTIALS_FILE

    # 1. Tentar baixar via API do Google Drive autenticada (Conta de Serviço) SOMENTE se for um ID nativo suportado por alt=media
    if creds_path.exists() and "drive.google.com" in url_str and file_id != "unknown":
        try:
            from google.oauth2.service_account import Credentials
            import google.auth.transport.requests

            scopes = ["https://www.googleapis.com/auth/drive.readonly", "https://www.googleapis.com/auth/drive"]
            credentials = Credentials.from_service_account_file(str(creds_path), scopes=scopes)
            auth_req = google.auth.transport.requests.Request()
            credentials.refresh(auth_req)
            
            headers = {"Authorization": f"Bearer {credentials.token}"}
            drive_api_url = f"https://www.googleapis.com/drive/v3/files/{file_id}?alt=media"

            res = requests.get(drive_api_url, headers=headers, stream=True, timeout=30)
            if res.status_code == 200:
                with open(local_filepath, "wb") as f:
                    for chunk in res.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                with open(local_filepath, "rb") as f:
                    head = f.read(512)
                    if b"<!DOCTYPE" not in head and b"<html" not in head:
                        logger.info(f"📥 Anexo baixado com sucesso via Conta de Serviço: {local_filepath.name}")
                        return str(local_filepath.resolve())
                os.remove(local_filepath)
        except Exception as e:
            logger.warning(f"Tentativa de download via API falhou: {e}")

    # 2. Tentar download via URL pública direta formatada (foto_url_direta)
    try:
        session = requests.Session()
        res = session.get(url_str, stream=True, timeout=30)

        if res.status_code == 200:
            with open(local_filepath, "wb") as f:
                for chunk in res.iter_content(chunk_size=8192):
                    f.write(chunk)

            # Validar se não baixou página HTML de erro/login
            with open(local_filepath, "rb") as f:
                head = f.read(512)
                if b"<!DOCTYPE" not in head and b"<html" not in head and len(head) > 50:
                    logger.info(f"📥 Anexo baixado via URL pública: {local_filepath.name}")
                    return str(local_filepath.resolve())
            
            os.remove(local_filepath)
            logger.warning(f"⚠️ O link do anexo retornou uma página bloqueada (HTML) em vez do arquivo. Verifique se o link está público.")
    except Exception as e:
        logger.warning(f"Erro ao baixar anexo público: {e}")

    return ""

class WhatsAppService:
    """
    Serviço responsável por disparar notificações via WhatsApp (OpenClaw / Gateway Webhook).
    Suporta envio de texto e anexos de imagem (foto_url).
    """

    def __init__(self):
        self.dry_run = settings.DRY_RUN
        self.api_url = settings.WHATSAPP_API_URL
        self.api_token = settings.WHATSAPP_API_TOKEN

    def enviar_cobranca(self, pendencia: Pendencia) -> bool:
        """
        Envia a mensagem individual para o contato do WhatsApp.
        """
        telefone_dest = pendencia.formatar_telefone_valido()
        if not telefone_dest:
            logger.warning(f"Telefone inválido ou não informado para Pendência {pendencia.pendencia_id} ({pendencia.nome_solicitante})")
            pendencia.status = "FALHA"
            pendencia.detalhes_envio = "Telefone inválido ou ausente"
            return False

        mensagem = formatar_mensagem_pendencia(
            nome_solicitante=pendencia.nome_solicitante,
            pendencia_id=pendencia.pendencia_id,
            descricao=pendencia.descricao,
            data_maxima=pendencia.data_maxima,
            hora_limite=pendencia.hora_limite,
            valor=pendencia.valor,
            codigo_barras=pendencia.codigo_barras
        )

        midia_anexo = baixar_anexo_drive(pendencia.foto_url_direta)

        if self.dry_run:
            info_foto = f"\n[Anexo]: {midia_anexo}" if midia_anexo else ""
            logger.info(f"[SIMULAÇÃO DRY_RUN] WhatsApp para {telefone_dest} (ID: {pendencia.pendencia_id}):\n---\n{mensagem}{info_foto}\n---")
            pendencia.status = "ENVIADO (SIMULAÇÃO)"
            pendencia.detalhes_envio = "Simulação concluída com sucesso (DRY_RUN=True)"
            return True

        # Envio Real via API / OpenClaw
        try:
            payload = {
                "number": telefone_dest,
                "message": mensagem,
                "token": self.api_token
            }
            if midia_anexo:
                payload["media_url"] = midia_anexo

            response = requests.post(self.api_url, json=payload, timeout=10)
            
            if response.status_code in (200, 201):
                logger.info(f"✅ Notificação WhatsApp enviada com sucesso para UC {pendencia.uc} ({telefone_dest})")
                pendencia.status = "ENVIADO"
                pendencia.detalhes_envio = f"Enviado via API - HTTP {response.status_code}"
                return True
            else:
                logger.error(f"❌ Falha no envio WhatsApp para UC {pendencia.uc}: HTTP {response.status_code} - {response.text}")
                pendencia.status = "FALHA"
                pendencia.detalhes_envio = f"Erro API HTTP {response.status_code}"
                return False

        except Exception as e:
            logger.error(f"Exceção ao disparar WhatsApp para UC {pendencia.uc}: {e}")
            pendencia.status = "FALHA"
            pendencia.detalhes_envio = f"Exceção: {str(e)}"
            return False
