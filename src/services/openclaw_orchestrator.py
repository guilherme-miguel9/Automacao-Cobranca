import pandas as pd
from datetime import datetime
from typing import Dict, List
from src.models.rota import Rota
from src.models.relatorio import RelatorioExecucao, ResumoRota
from src.services.whatsapp_service import WhatsAppService
from src.services.email_service import EmailService
from src.utils.logger import logger
from config.settings import settings

class OpenClawOrchestrator:
    """
    Orquestrador principal de cobranças e rotas do OpenClaw.
    Gerencia a execução sequencial por rotas, envios de WhatsApp, e-mails de acompanhamento
    e consolidação de relatórios de auditoria.
    """

    def __init__(self):
        self.whatsapp_service = WhatsAppService()
        self.email_service = EmailService()

    def executar_fluxo_cobranca(self, rotas: Dict[str, Rota]) -> RelatorioExecucao:
        """
        Executa o fluxo completo de cobrança para todas as rotas ativas.
        """
        logger.info("==================================================")
        logger.info("INICIANDO EXECUCAO DO ROBO DE COBRANCAS OPENCLAW")
        logger.info(f"Modo de Execucao: {'DRY_RUN (SIMULACAO)' if settings.DRY_RUN else 'REAL (PRODUCAO)'}")
        logger.info("==================================================")

        total_processado = 0
        total_sucesso = 0
        total_falha = 0
        valor_total_acumulado = 0.0

        resumo_rotas: Dict[str, ResumoRota] = {}
        supervisores_notificar = set()

        for cod_rota, rota in rotas.items():
            logger.info(f"\n---> Processando Rota: {cod_rota} ({rota.regiao}) - {rota.quantidade_pendencias()} pendencias")
            
            sucessos_rota = 0
            falhas_rota = 0
            valor_rota = rota.total_valor_pendente()
            valor_sucesso_rota = 0.0

            # 1. Enviar notificações via WhatsApp cliente a cliente
            import time
            import random

            for pendencia in rota.pendencias:
                total_processado += 1
                valor_total_acumulado += pendencia.valor

                # Verificar se o encarregado deu OK ou marcou como concluído no Sheets
                if pendencia.esta_concluido():
                    logger.info(f"Ignorando pendencia {pendencia.pendencia_id} ({pendencia.nome_solicitante}): Marcada como OK no Sheets.")
                    pendencia.detalhes_envio = "Ignorado: Status OK no Sheets"
                    sucessos_rota += 1
                    total_sucesso += 1
                    continue

                # Verificar se a Data/Hora Máxima foi ultrapassada
                if pendencia.data_maxima_expirada():
                    logger.info(f"Ignorando pendencia {pendencia.pendencia_id} ({pendencia.nome_solicitante}): Data Maxima ({pendencia.data_maxima}) ultrapassada.")
                    pendencia.detalhes_envio = f"Ignorado: Data Maxima Expirada ({pendencia.data_maxima})"
                    falhas_rota += 1
                    total_falha += 1
                    continue

                # Verificar se já foi enviada hoje
                if pendencia.ja_enviado_hoje():
                    logger.info(f"Ignorando pendencia {pendencia.pendencia_id} ({pendencia.nome_solicitante}): Já enviada hoje.")
                    pendencia.detalhes_envio = "Ignorado: Já enviado hoje"
                    sucessos_rota += 1
                    total_sucesso += 1
                    continue

                # Verificar se existe uma data programada e se hoje é o dia correto
                if not pendencia.pode_enviar_hoje():
                    logger.info(f"Ignorando pendencia {pendencia.pendencia_id} ({pendencia.nome_solicitante}): Fora do horario programado ou janela automatica.")
                    pendencia.detalhes_envio = f"Ignorado: Fora do horario/janela"
                    # Para não contabilizar como falha dura no report, você pode tratar como sucesso pulado ou falha.
                    # Mas como ele não enviou ainda e não deve, vamos registrar como sucesso na leitura mas sem envio (ou falha técnica).
                    # A melhor forma é registrar nos detalhes e continuar, mas mantendo a lógica de falhas_rota para ele tentar amanhã de novo.
                    falhas_rota += 1
                    total_falha += 1
                    continue

                # Variação de tempo aleatória entre envios (Antispam WhatsApp: 3 a 8 segundos)
                delay_antispam = random.uniform(3.0, 8.0)
                logger.info(f"Variacao antispam: aguardando {delay_antispam:.1f}s antes de notificar {pendencia.nome_solicitante}...")
                time.sleep(delay_antispam)

                sucesso = self.whatsapp_service.enviar_cobranca(pendencia)
                if sucesso:
                    pendencia.registrar_envio()
                    sucessos_rota += 1
                    total_sucesso += 1
                    valor_sucesso_rota += pendencia.valor
                else:
                    falhas_rota += 1
                    total_falha += 1

            # Guardar resumo da rota
            resumo_rotas[cod_rota] = ResumoRota(
                codigo_rota=cod_rota,
                regiao=rota.regiao,
                total_cobranças=rota.quantidade_pendencias(),
                sucessos=sucessos_rota,
                falhas=falhas_rota,
                valor_total=valor_rota,
                valor_sucesso=valor_sucesso_rota
            )

            # 2. Enviar e-mail de resumo da rota para o Encarregado
            self.email_service.enviar_resumo_encarregado(rota)

            # Guardar supervisor para relatório regional
            if rota.supervisor and rota.supervisor.email:
                supervisores_notificar.add(rota.supervisor.email)

        # 3. Criar Relatório Consolidado de Execução
        relatorio = RelatorioExecucao(
            data_execucao=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            total_processado=total_processado,
            total_sucesso=total_sucesso,
            total_falha=total_falha,
            valor_total_pendencias=valor_total_acumulado,
            resumo_por_rota=resumo_rotas
        )

        # 4. Enviar Relatório Regional aos Supervisores
        for email_sup in supervisores_notificar:
            self.email_service.enviar_relatorio_supervisor(email_sup, relatorio)

        # 5. Exportar relatório consolidado em CSV
        self._exportar_planilha_resultado(rotas)

        logger.info("\n==================================================")
        logger.info(f"PROCESSAMENTO CONCLUIDO COM SUCESSO!")
        logger.info(f"Total Processado: {total_processado} | Sucessos: {total_sucesso} | Falhas: {total_falha}")
        logger.info("==================================================")

        return relatorio

    def _exportar_planilha_resultado(self, rotas: Dict[str, Rota]):
        """
        # ponytail: Export em CSV nativo elimina dependência de libs Excel (openpyxl).
        Salva o resultado consolidado em um arquivo CSV no diretório data/output/.
        """
        try:
            linhas = []
            for cod_rota, rota in rotas.items():
                for p in rota.pendencias:
                    linhas.append({
                        "Data Execução": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Rota": cod_rota,
                        "Região": rota.regiao,
                        "UC": p.uc,
                        "Cliente": p.cliente_nome,
                        "Telefone": p.telefone,
                        "E-mail": p.email or "",
                        "Valor (R$)": p.valor,
                        "Vencimento": p.vencimento,
                        "Status Envio": p.status,
                        "Detalhes": p.detalhes_envio,
                        "Encarregado": rota.encarregado.nome,
                        "Supervisor": rota.supervisor.nome
                    })

            df_out = pd.DataFrame(linhas)
            data_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            arquivo_saida = settings.OUTPUT_DIR / f"resultado_cobranca_{data_str}.csv"
            
            df_out.to_csv(arquivo_saida, index=False, encoding="utf-8-sig")
            logger.info(f"📊 Relatório consolidado em CSV salvo em: {arquivo_saida}")
        except Exception as e:
            logger.error(f"Erro ao exportar relatório de resultado: {e}")

