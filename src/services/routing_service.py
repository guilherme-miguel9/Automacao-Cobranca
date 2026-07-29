from typing import List, Dict
from src.models.pendencia import Pendencia
from src.models.rota import Rota, ContatoHierarquia
from src.utils.logger import logger

class RoutingService:
    """
    Serviço responsável por categorizar as pendências por rotas operacionais
    e vincular a hierarquia de contatos (Encarregado, Operador e Supervisor).
    """

    def __init__(self, mapa_hierarquia: Dict[str, dict] = None):
        self.mapa_hierarquia = mapa_hierarquia or {}

    def agrupar_por_rotas(self, pendencias: List[Pendencia]) -> Dict[str, Rota]:
        """
        Agrupa uma lista de pendências por código de rota e constrói a estrutura de objetos Rota.
        """
        logger.info(f"Iniciando agrupamento de {len(pendencias)} pendências em suas respectivas rotas.")
        rotas: Dict[str, Rota] = {}

        for pendencia in pendencias:
            cod_rota = pendencia.rota_codigo or "ROTA_PADRAO"
            nome_solic = (pendencia.nome_solicitante or "").strip().lower()

            # Buscar contatos por código de rota ou por nome do solicitante
            info_h = self.mapa_hierarquia.get(cod_rota) or self.mapa_hierarquia.get(nome_solic, {})

            # Se o telefone estiver ausente na pendência, preencher com o telefone do contato encontrado
            if not pendencia.telefone and info_h.get("encarregado_telefone"):
                pendencia.telefone = info_h.get("encarregado_telefone")
                logger.info(f"🔍 Telefone do solicitante '{pendencia.nome_solicitante}' localizado na aba Contatos: {pendencia.telefone}")

            if cod_rota not in rotas:
                encarregado = ContatoHierarquia(
                    nome=info_h.get("encarregado_nome", pendencia.nome_solicitante or f"Encarregado {cod_rota}"),
                    email=info_h.get("encarregado_email", "encarregado@empresa.com.br"),
                    telefone=info_h.get("encarregado_telefone", pendencia.telefone)
                )
                
                operador = ContatoHierarquia(
                    nome=info_h.get("operador_nome", f"Operador {cod_rota}"),
                    email=info_h.get("operador_email", "operador@empresa.com.br"),
                    telefone=info_h.get("operador_telefone", "")
                )
                
                supervisor = ContatoHierarquia(
                    nome=info_h.get("supervisor_nome", "Supervisor Regional"),
                    email=info_h.get("supervisor_email", "supervisor@empresa.com.br"),
                    telefone=info_h.get("supervisor_telefone", "")
                )

                rotas[cod_rota] = Rota(
                    codigo=cod_rota,
                    regiao=info_h.get("regiao", "Região Operacional"),
                    encarregado=encarregado,
                    operador=operador,
                    supervisor=supervisor,
                    pendencias=[]
                )

            rotas[cod_rota].pendencias.append(pendencia)

        logger.info(f"✅ Pendências agrupadas com sucesso em {len(rotas)} rotas ativas.")
        return rotas
