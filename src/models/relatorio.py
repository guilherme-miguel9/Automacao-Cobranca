from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class ResumoRota:
    codigo_rota: str
    regiao: str
    total_cobranças: int
    sucessos: int
    falhas: int
    valor_total: float
    valor_sucesso: float

@dataclass
class RelatorioExecucao:
    data_execucao: str
    total_processado: int
    total_sucesso: int
    total_falha: int
    valor_total_pendencias: float
    resumo_por_rota: Dict[str, ResumoRota] = field(default_factory=dict)
