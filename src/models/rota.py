from dataclasses import dataclass, field
from typing import List
from src.models.pendencia import Pendencia

@dataclass
class ContatoHierarquia:
    nome: str
    email: str
    telefone: str = ""

@dataclass
class Rota:
    codigo: str                             # Identificador único da Rota (ex: ROTA_101)
    regiao: str                             # Nome da Região / Município
    encarregado: ContatoHierarquia           # Encarregado da Rota
    operador: ContatoHierarquia              # Operador/Cobrador responsável pela Rota
    supervisor: ContatoHierarquia            # Supervisor da Região
    pendencias: List[Pendencia] = field(default_factory=list) # Lista de pendências atribuídas

    def total_valor_pendente(self) -> float:
        return sum(p.valor for p in self.pendencias)

    def quantidade_pendencias(self) -> int:
        return len(self.pendencias)
