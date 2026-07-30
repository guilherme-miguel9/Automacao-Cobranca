import pandas as pd
from typing import List, Dict
from pathlib import Path
from src.models.pendencia import Pendencia
from src.utils.logger import logger
from config.settings import settings

class GoogleSheetsConnector:
    """
    # ponytail: Fonte de dados única (Google Sheets online). Abstração YAGNI simplificada.
    Conector exclusivo para leitura e sincronização com Google Sheets online.
    Suporta autenticação via API de Conta de Serviço (gspread).
    """

    def __init__(self, credentials_path: Path = None, spreadsheet_name: str = None):
        self.credentials_path = credentials_path or settings.GOOGLE_CREDENTIALS_FILE
        self.spreadsheet_name = spreadsheet_name or settings.GSHEET_SPREADSHEET_NAME
        self.client = None

    def conectar(self) -> bool:
        """
        Estabelece conexão com a API do Google Sheets.
        """
        if not self.credentials_path.exists():
            logger.warning(
                f"Arquivo de credenciais do Google Sheets não encontrado em: {self.credentials_path}.\n"
                f"Para usar a API oficial do Google Sheets, salve a chave JSON da Conta de Serviço nesta pasta."
            )
            return False

        try:
            import gspread
            from google.oauth2.service_account import Credentials

            scopes = [
                "https://www.googleapis.com/auth/spreadsheets",
                "https://www.googleapis.com/auth/drive"
            ]
            creds = Credentials.from_service_account_file(self.credentials_path, scopes=scopes)
            self.client = gspread.authorize(creds)
            logger.info("Conectado à API do Google Sheets com sucesso.")
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar com Google Sheets: {e}")
            return False

    def _abrir_planilha(self):
        """
        Abre a planilha por URL, por ID/Chave ou por Nome exato.
        """
        nome_ou_url = str(self.spreadsheet_name).strip()
        if nome_ou_url.startswith("http://") or nome_ou_url.startswith("https://"):
            return self.client.open_by_url(nome_ou_url)
        elif len(nome_ou_url) >= 30 and "/" not in nome_ou_url and " " not in nome_ou_url:
            try:
                return self.client.open_by_key(nome_ou_url)
            except Exception:
                return self.client.open(nome_ou_url)
        else:
            return self.client.open(nome_ou_url)

    def ler_pendencias(self) -> List[Pendencia]:
        """
        Lê todas as pendências ativas da planilha online do Google Sheets.
        """
        if not self.client and not self.conectar():
            logger.error("Falha na conexão com Google Sheets. Verifique a chave JSON em config/google_credentials.json.")
            return []

        try:
            spreadsheet = self._abrir_planilha()
            # Tentar abrir a aba 'Pendencias' ou usar a primeira aba
            try:
                sheet = spreadsheet.worksheet("Pendencias")
            except Exception:
                sheet = spreadsheet.sheet1

            records = sheet.get_all_records()

            pendencias = []
            for row in records:
                row_norm = {str(k).strip().lower().replace(" ", "_"): v for k, v in row.items()}
                
                try:
                    p = Pendencia(
                        pendencia_id=str(row_norm.get("pendencia", row_norm.get("uc", row_norm.get("contrato", "PEND-001")))).strip(),
                        nome_solicitante=str(row_norm.get("nome_solicitante", row_norm.get("solicitante", row_norm.get("cliente_nome", "Solicitante")))).strip(),
                        descricao=str(row_norm.get("descrição", row_norm.get("descricao", row_norm.get("detalhes", "Sem descrição")))).strip(),
                        data_maxima=str(row_norm.get("data_máxima", row_norm.get("data_maxima", row_norm.get("vencimento", "")))).strip(),
                        telefone=str(row_norm.get("telefone", row_norm.get("celular", row_norm.get("whatsapp", "")))).strip(),
                        foto_url=str(row_norm.get("anexo", row_norm.get("anexo_url", row_norm.get("foto", row_norm.get("foto_url", row_norm.get("imagem", "")))))).strip(),
                        email=str(row_norm.get("email", "")) if row_norm.get("email") else None,
                        valor=float(row_norm.get("valor", row_norm.get("valor_pendente", 0.0))) if row_norm.get("valor") else 0.0,
                        rota_codigo=str(row_norm.get("rota_codigo", row_norm.get("rota", "ROTA_PADRAO"))).strip(),
                        hora_limite=str(row_norm.get("hora_limite", row_norm.get("hora_máxima", row_norm.get("hora_maxima", row_norm.get("hora", row_norm.get("horário", row_norm.get("horario", ""))))))).strip(),
                        codigo_barras=str(row_norm.get("codigo_barras", row_norm.get("pix", ""))) if row_norm.get("codigo_barras", row_norm.get("pix", "")) else "",
                        status=str(row_norm.get("status", row_norm.get("ok", row_norm.get("confirmado", row_norm.get("resposta", row_norm.get("situação", row_norm.get("situacao", "PENDENTE"))))))).strip(),
                        mensagem_programada=str(row_norm.get("mensagem_programada", row_norm.get("agendamento", ""))).strip()
                    )
                    pendencias.append(p)
                except Exception as ex:
                    logger.warning(f"Ignorando linha inválida no Google Sheets: {ex}")

            logger.info(f"✅ {len(pendencias)} pendências lidas com sucesso do Google Sheets.")
            return pendencias
        except Exception as e:
            import traceback
            logger.error(f"Erro ao ler dados do Google Sheets: {e}\n{traceback.format_exc()}")
            return []

    def ler_hierarquia_rotas(self) -> Dict[str, dict]:
        """
        Lê a aba 'Rotas' ou 'Contatos' no Google Sheets para extrair a hierarquia (Encarregado e Supervisor).
        """
        if not self.client and not self.conectar():
            return {}

        try:
            spreadsheet = self._abrir_planilha()
            sheet = None
            for nome_aba in ["Rotas", "Contatos", "Hierarquia"]:
                try:
                    sheet = spreadsheet.worksheet(nome_aba)
                    break
                except Exception:
                    pass

            if not sheet:
                logger.info("Aba 'Rotas' ou 'Contatos' não localizada no Google Sheets. Usando hierarquia padrão.")
                return {}

            records = sheet.get_all_records()
            mapa_rotas = {}

            for row in records:
                row_norm = {str(k).strip().lower().replace(" ", "_"): v for k, v in row.items()}
                codigo = str(row_norm.get("rota_codigo", row_norm.get("rota", ""))).strip()
                nome = str(row_norm.get("encarregado_nome", row_norm.get("nome", row_norm.get("nome_solicitante", row_norm.get("contato", ""))))).strip()
                telefone = str(row_norm.get("encarregado_telefone", row_norm.get("telefone", row_norm.get("celular", row_norm.get("whatsapp", ""))))).strip()

                dados_contato = {
                    "regiao": str(row_norm.get("regiao", "Região Principal")).strip(),
                    "encarregado_nome": nome or "Encarregado",
                    "encarregado_telefone": telefone,
                    "encarregado_email": str(row_norm.get("encarregado_email", row_norm.get("email", ""))).strip(),
                    "operador_nome": str(row_norm.get("operador_nome", "Operador")).strip(),
                    "operador_email": str(row_norm.get("operador_email", "")).strip(),
                    "operador_telefone": str(row_norm.get("operador_telefone", "")).strip(),
                    "supervisor_nome": str(row_norm.get("supervisor_nome", "Supervisor")).strip(),
                    "supervisor_email": str(row_norm.get("supervisor_email", "")).strip(),
                }

                if codigo:
                    mapa_rotas[codigo] = dados_contato
                if nome:
                    # Indexar também pelo nome do contato (normalizado em caixa baixa)
                    mapa_rotas[nome.lower()] = dados_contato

            logger.info(f"✅ {len(records)} contatos/rotas lidos e indexados do Google Sheets.")
            return mapa_rotas

        except Exception as e:
            logger.warning(f"Erro ao ler hierarquia de contatos/rotas do Google Sheets: {e}")
            return {}
