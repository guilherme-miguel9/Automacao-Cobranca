import sys
from config.settings import settings
from src.connectors.gsheets_connector import GoogleSheetsConnector
from src.services.routing_service import RoutingService
from src.services.openclaw_orchestrator import OpenClawOrchestrator
from src.utils.logger import logger

def main():
    logger.info("==================================================")
    logger.info("Iniciando Robô de Automação de Cobranças (Google Sheets + OpenClaw)")
    logger.info("==================================================")

    # 1. Carregar pendências e rotas exclusivamente do Google Sheets online
    logger.info(f"Conectando ao Google Sheets: Planilha '{settings.GSHEET_SPREADSHEET_NAME}'...")
    gsheets = GoogleSheetsConnector()

    pendencias = gsheets.ler_pendencias()
    mapa_hierarquia = gsheets.ler_hierarquia_rotas()

    if not pendencias:
        logger.error(
            "⚠️ Nenhuma pendência foi localizada no Google Sheets!\n"
            "Verifique se:\n"
            "1. O arquivo 'config/google_credentials.json' com as credenciais da Conta de Serviço existe.\n"
            "2. A planilha no Google Sheets foi compartilhada com o e-mail da Conta de Serviço.\n"
            f"3. O nome da planilha em 'config/.env' bate exatamente com '{settings.GSHEET_SPREADSHEET_NAME}'."
        )
        sys.exit(1)

    # 2. Agrupar Pendências por Rotas e Mapear Hierarquia (Encarregado, Operador, Supervisor)
    routing_service = RoutingService(mapa_hierarquia=mapa_hierarquia)
    rotas = routing_service.agrupar_por_rotas(pendencias)

    # 3. Executar o Orquestrador OpenClaw
    orchestrator = OpenClawOrchestrator()
    relatorio = orchestrator.executar_fluxo_cobranca(rotas)

    logger.info("Execução finalizada com sucesso!")

if __name__ == "__main__":
    main()
