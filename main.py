import sys
from config.settings import settings
from src.connectors.gsheets_connector import GoogleSheetsConnector
from src.services.routing_service import RoutingService
from src.services.openclaw_orchestrator import OpenClawOrchestrator
from src.utils.logger import logger

import time
import random
from datetime import datetime
from config.settings import settings
from src.connectors.gsheets_connector import GoogleSheetsConnector
from src.services.routing_service import RoutingService
from src.services.openclaw_orchestrator import OpenClawOrchestrator
from src.utils.logger import logger

def executar_ciclo():
    logger.info("==================================================")
    logger.info("Iniciando Robô de Automação de Cobranças (Google Sheets + OpenClaw)")
    logger.info("==================================================")

    # 1. Carregar pendências e rotas exclusivamente do Google Sheets online
    logger.info(f"Conectando ao Google Sheets: Planilha '{settings.GSHEET_SPREADSHEET_NAME}'...")
    gsheets = GoogleSheetsConnector()

    pendencias = gsheets.ler_pendencias()
    mapa_hierarquia = gsheets.ler_hierarquia_rotas()

    if not pendencias:
        logger.warning("Nenhuma pendência para processar neste ciclo.")
        return

    # 2. Agrupar Pendências por Rotas e Mapear Hierarquia
    routing_service = RoutingService(mapa_hierarquia=mapa_hierarquia)
    rotas = routing_service.agrupar_por_rotas(pendencias)

    # 3. Executar o Orquestrador OpenClaw com checagem de OK, Data Máxima e Antispam
    orchestrator = OpenClawOrchestrator()
    orchestrator.executar_fluxo_cobranca(rotas)
    logger.info("Ciclo de execução finalizado com sucesso!")

def modo_agendado():
    """
    Executa o robô continuamente nas janelas das 08h, 11h, 14h e 17h com variação aleatória de horário (antispam).
    """
    logger.info("⏰ MODO AGENDADO ATIVO: O robô rodará nas janelas de 08h, 11h, 14h e 17h com variação antispam.")
    janelas_disparo = ["08", "11", "14", "17"]
    janelas_executadas_hoje = set()
    dia_atual = datetime.now().day

    while True:
        agora = datetime.now()

        # Resetar janelas executadas no novo dia
        if agora.day != dia_atual:
            dia_atual = agora.day
            janelas_executadas_hoje.clear()

        hora_str = agora.strftime("%H")

        if hora_str in janelas_disparo and hora_str not in janelas_executadas_hoje:
            # Jitter aleatório de 1 a 15 minutos para simular comportamento humano
            jitter_minutos = random.randint(1, 15)
            logger.info(f"🎯 Janela das {hora_str}h identificada. Aplicando variação antispam de {jitter_minutos} minutos antes de iniciar...")
            time.sleep(jitter_minutos * 60)

            executar_ciclo()
            janelas_executadas_hoje.add(hora_str)

        time.sleep(60)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        modo_agendado()
    else:
        executar_ciclo()

if __name__ == "__main__":
    main()
