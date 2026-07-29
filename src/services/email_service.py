import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from src.models.rota import Rota
from src.models.relatorio import RelatorioExecucao
from src.utils.formatters import formatar_moeda
from src.utils.logger import logger
from config.settings import settings

class EmailService:
    """
    Serviço responsável pelo envio de e-mails informativos e relatórios consolidados
    para Encarregados de Rota e Supervisores Regionais.
    """

    def __init__(self):
        self.dry_run = settings.DRY_RUN
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_pass = settings.SMTP_PASSWORD
        self.from_name = settings.EMAIL_FROM_NAME

    def enviar_resumo_encarregado(self, rota: Rota) -> bool:
        """
        Envia um e-mail de resumo para o Encarregado da Rota com o status das cobranças processadas.
        """
        destinatario = rota.encarregado.email
        if not destinatario:
            logger.warning(f"E-mail do Encarregado da Rota {rota.codigo} não cadastrado.")
            return False

        assunto = f"[Relatório de Cobrança] Status da Rota {rota.codigo} - {rota.regiao}"
        
        conteudo_body = (
            f"Olá, {rota.encarregado.nome}!\n\n"
            f"Segue o resumo do processamento de cobranças para a sua rota:\n"
            f"--------------------------------------------------\n"
            f"📍 Rota: {rota.codigo} ({rota.regiao})\n"
            f"📋 Quantidade de Pendências: {rota.quantidade_pendencias()}\n"
            f"💰 Valor Total Pendente: {formatar_moeda(rota.total_valor_pendente())}\n"
            f"👤 Operador Responsável: {rota.operador.nome}\n"
            f"--------------------------------------------------\n\n"
            f"Detalhamento por Cliente:\n"
        )

        for p in rota.pendencias:
            conteudo_body += f"• UC {p.uc} | {p.cliente_nome} | {formatar_moeda(p.valor)} | Status: {p.status}\n"

        conteudo_body += "\nAtenciosamente,\nRobô de Cobranças"

        return self._enviar_email(destinatario, assunto, conteudo_body)

    def enviar_relatorio_supervisor(self, email_supervisor: str, relatorio: RelatorioExecucao) -> bool:
        """
        Envia o relatório executivo consolidado da região para o Supervisor.
        """
        if not email_supervisor:
            logger.warning("E-mail do Supervisor não informado.")
            return False

        assunto = f"📊 [Relatório Executivo Regional] Cobranças - {relatorio.data_execucao}"

        conteudo_body = (
            f"Prezado(a) Supervisor(a),\n\n"
            f"Apresentamos o relatório consolidado do processamento de cobranças em sua região:\n\n"
            f"--------------------------------------------------\n"
            f"📅 Data da Execução: {relatorio.data_execucao}\n"
            f"🔢 Total de Pendências Processadas: {relatorio.total_processado}\n"
            f"✅ Notificações Enviadas com Sucesso: {relatorio.total_sucesso}\n"
            f"❌ Falhas no Envio: {relatorio.total_falha}\n"
            f"💵 Montante Total em Cobrança: {formatar_moeda(relatorio.valor_total_pendencias)}\n"
            f"--------------------------------------------------\n\n"
            f"Resumo por Rota Operacional:\n"
        )

        for cod_rota, resumo in relatorio.resumo_por_rota.items():
            conteudo_body += (
                f"\n📌 Rota: {cod_rota} ({resumo.regiao})\n"
                f"   - Total: {resumo.total_cobranças} pendências | Sucessos: {resumo.sucessos} | Falhas: {resumo.falhas}\n"
                f"   - Valor Processado: {formatar_moeda(resumo.valor_total)}\n"
            )

        conteudo_body += "\nAtenciosamente,\nSistema de Automação de Cobranças"

        return self._enviar_email(email_supervisor, assunto, conteudo_body)

    def _enviar_email(self, destinatario: str, assunto: str, corpo: str) -> bool:
        if self.dry_run:
            logger.info(f"[SIMULAÇÃO DRY_RUN] Envio de E-mail para '{destinatario}':\nAssunto: {assunto}\nCorpo:\n{corpo}\n")
            return True

        try:
            msg = MIMEMultipart()
            msg["From"] = f"{self.from_name} <{self.smtp_user}>"
            msg["To"] = destinatario
            msg["Subject"] = assunto
            msg.attach(MIMEText(corpo, "plain", "utf-8"))

            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_pass)
                server.send_message(msg)

            logger.info(f"✅ E-mail enviado com sucesso para {destinatario}")
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar e-mail para {destinatario}: {e}")
            return False
