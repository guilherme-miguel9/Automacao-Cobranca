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
    Executa o robô continuamente. 
    A inteligência de janelas (automáticas) e horários exatos (programados) está no modelo Pendencia.
    Verifica a cada 1 minuto (60 segundos).
    """
    logger.info("⏰ MODO AGENDADO ATIVO: O robô ficará verificando a planilha a cada 1 minuto.")

    while True:
        try:
            executar_ciclo()
        except Exception as e:
            logger.error(f"Erro no ciclo de verificação: {e}")
        
        # Pausa 1 minuto entre checagens
        time.sleep(60)

def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        modo_agendado()
    else:
        executar_ciclo()

if __name__ == "__main__":
    main()
