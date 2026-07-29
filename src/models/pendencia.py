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

    def formatar_telefone_valido(self) -> str:
        from src.utils.formatters import formatar_telefone
        return formatar_telefone(self.telefone)

