from dataclasses import dataclass
from typing import Optional

@dataclass
class Pendencia:
    pendencia_id: str                   # Código/ID da Pendência (ex: PEND-102)
    nome_solicitante: str               # Nome do Solicitante / Cliente
    descricao: str                      # Descrição detalhada da pendência
    data_maxima: str                    # Data Máxima de atendimento/vencimento
    telefone: str                       # Telefone / WhatsApp de contato
    foto_url: Optional[str] = ""        # URL da imagem/foto a ser enviada no WhatsApp (opcional)
    email: Optional[str] = None         # E-mail do Solicitante (opcional)
    valor: float = 0.0                  # Valor da pendência (opcional)
    rota_codigo: str = "ROTA_PADRAO"    # Código da Rota / Setor
    hora_limite: Optional[str] = ""     # Hora Limite (ex: 17:00)
    codigo_barras: Optional[str] = ""   # Código de Barras / Chave PIX (opcional)
    status: str = "PENDENTE"            # Status: PENDENTE, ENVIADO, FALHA
    detalhes_envio: Optional[str] = ""   # Log de envio
    mensagem_programada: Optional[str] = "" # Data para disparo programado (opcional)

    @property
    def foto_url_direta(self) -> str:
        """
        Converte URLs de visualização do Google Drive para links diretos de download (suporta imagens, PDFs, documentos).
        """
        if not self.foto_url:
            return ""
        url = str(self.foto_url).strip()
        import re
        # Extrai o ID de links do drive (file/d/, id=, ou docs.google.com/.../d/)
        drive_match = re.search(r"(?:file/d/|id=|/d/)([\w-]+)", url)
        if drive_match and ("drive.google.com" in url or "docs.google.com" in url):
            file_id = drive_match.group(1)
            
            # O usuário informou que planilhas estão falhando com export?format=xlsx porque muitas vezes são arquivos .xlsx upados
            # Vamos usar o padrão do Google Drive para todas as planilhas/documentos também
            if "spreadsheets" in url:
                return f"https://drive.google.com/uc?export=download&id={file_id}&ext=xlsx"
            elif "document" in url:
                return f"https://drive.google.com/uc?export=download&id={file_id}&ext=pdf"
            else:
                return f"https://drive.google.com/uc?export=download&id={file_id}"
        return url

    @property
    def uc(self) -> str:
        return self.pendencia_id

    @property
    def cliente_nome(self) -> str:
        return self.nome_solicitante

    @property
    def vencimento(self) -> str:
        return self.data_maxima

    def esta_concluido(self) -> bool:
        st = str(self.status or "").strip().upper()
        return st in ["OK", "CONCLUIDO", "CONCLUÍDO", "FINALIZADO", "CONFIRMADO", "PAGO", "RESOLVIDO", "SIM", "YES"]

    def data_maxima_expirada(self) -> bool:
        """
        Verifica se a data/hora atual ultrapassou a Data Máxima / Hora Limite configurada.
        """
        if not self.data_maxima:
            return False

        try:
            from datetime import datetime
            dt_str = str(self.data_maxima).strip()
            
            # Se hora_limite existir e não estiver na data_maxima, concatenar
            if self.hora_limite and ":" in str(self.hora_limite) and len(dt_str) <= 10:
                dt_str = f"{dt_str} {str(self.hora_limite).strip()}"

            dt_max = None
            for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(dt_str, fmt)
                    if fmt in ("%d/%m/%Y", "%Y-%m-%d") and not self.hora_limite:
                        dt = dt.replace(hour=23, minute=59, second=59)
                    dt_max = dt
                    break
                except ValueError:
                    continue

            if dt_max and datetime.now() > dt_max:
                return True
        except Exception:
            pass

        return False

    def pode_enviar_hoje(self) -> bool:
        """
        Verifica se a mensagem tem uma data/hora programada.
        Se não tiver (vazia), retorna True (pode enviar qualquer hora, segue agendamento automático).
        Se tiver apenas data, só retorna True se for o dia exato de hoje.
        Se tiver data e hora, só retorna True se o momento atual for maior ou igual à data e hora programada.
        """
        dt_str = str(self.mensagem_programada or "").strip()
        if not dt_str:
            return True

        from datetime import datetime
        try:
            # Tentar formatos com Hora e Minuto
            for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
                try:
                    dt_prog = datetime.strptime(dt_str, fmt)
                    # Tem hora! Só envia se passou do momento exato programado
                    return datetime.now() >= dt_prog
                except ValueError:
                    continue
            
            # Tentar formatos somente com Data
            for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
                try:
                    dt_prog = datetime.strptime(dt_str, fmt).date()
                    # Não tem hora, só data. Envia em qualquer momento daquele dia (desde as 00:00).
                    return dt_prog == datetime.now().date()
                except ValueError:
                    continue

        except Exception:
            pass

        return True # Se houver erro de formatação absurdo, melhor tentar enviar do que ignorar para sempre

    def formatar_telefone_valido(self) -> str:
        from src.utils.formatters import formatar_telefone
        return formatar_telefone(self.telefone)

