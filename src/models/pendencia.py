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
    codigo_barras: Optional[str] = ""   # Código de Barras / Chave PIX (opcional)
    status: str = "PENDENTE"            # Status: PENDENTE, ENVIADO, FALHA
    detalhes_envio: Optional[str] = ""   # Log de envio

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
        Verifica se a data/hora atual ultrapassou a Data Máxima configurada.
        Suporta formatos: 'DD/MM/YYYY', 'DD/MM/YYYY HH:MM', 'YYYY-MM-DD', 'YYYY-MM-DD HH:MM'.
        """
        if not self.data_maxima:
            return False

        try:
            from datetime import datetime
            dt_str = str(self.data_maxima).strip()
            dt_max = None
            
            for fmt in ("%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S", "%d/%m/%Y", "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                try:
                    dt = datetime.strptime(dt_str, fmt)
                    if fmt in ("%d/%m/%Y", "%Y-%m-%d"):
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

    def formatar_telefone_valido(self) -> str:
        from src.utils.formatters import formatar_telefone
        return formatar_telefone(self.telefone)

