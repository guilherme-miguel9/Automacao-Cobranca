import requests
from src.models.pendencia import Pendencia
from src.utils.formatters import formatar_mensagem_pendencia
from src.utils.logger import logger
from config.settings import settings

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

        midia_anexo = pendencia.foto_url_direta

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
