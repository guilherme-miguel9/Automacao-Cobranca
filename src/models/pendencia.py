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
    linha_planilha: int = 0             # Índice da linha na planilha (para diferenciar duplicatas)

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
        Se existir uma mensagem programada manualmente, ignora a data máxima.
        """
        if self.mensagem_programada and str(self.mensagem_programada).strip():
            return False

        if not self.data_maxima:
            return False

        try:
            from datetime import datetime
            import re

            dt_str = str(self.data_maxima).strip()
            clean_dt = dt_str.lower().replace("às", "").replace("as", "").strip()
            clean_dt = re.sub(r'(\d{1,2})\s*h\s*(\d{2})', r'\1:\2', clean_dt)
            clean_dt = re.sub(r'(\d{1,2})\s*h\b', r'\1:00', clean_dt)

            # Se hora_limite existir e não estiver em data_maxima, concatenar
            if self.hora_limite and ":" in str(self.hora_limite) and len(clean_dt) <= 10:
                clean_dt = f"{clean_dt} {str(self.hora_limite).strip()}"

            dt_max = None
            for fmt in (
                "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S",
                "%d/%m/%y %H:%M", "%d/%m/%y %H:%M:%S",
                "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S",
                "%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"
            ):
                try:
                    dt = datetime.strptime(clean_dt, fmt)
                    # Se for apenas data sem horário especifico, vai até o fim do dia de vencimento (23:59:59)
                    if fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d") and not self.hora_limite:
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

    def obter_hora_limite_data_maxima(self) -> str:
        """
        Extrai a hora (00-23) de data_maxima ou hora_limite se houver horário específico.
        """
        import re
        texto = f"{self.data_maxima or ''} {self.hora_limite or ''}".lower().replace("às", "").replace("as", "").strip()
        match = re.search(r'(\d{1,2})\s*:\s*\d{2}', texto)
        if not match:
            match = re.search(r'(\d{1,2})\s*h', texto)
        if match:
            h = int(match.group(1))
            return f"{h:02d}"
        return ""

    def _obter_chave_cache(self) -> str:
        if self.linha_planilha > 0:
            chave_base = f"{self.pendencia_id}_L{self.linha_planilha}"
        else:
            chave_base = self.pendencia_id

        dt_prog = str(self.mensagem_programada or "").strip()
        if not dt_prog:
            from datetime import datetime
            hora_str = datetime.now().strftime("%H")
            return f"{chave_base}_H{hora_str}"

        return chave_base

    def ja_enviado_hoje(self) -> bool:
        from datetime import datetime
        from config.settings import settings
        import json
        
        hoje = datetime.now().strftime("%Y-%m-%d")
        cache_file = settings.APP_DIR / "config" / "envios_cache.json"
        try:
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            else:
                cache = {}
            if cache.get("data") != hoje:
                return False
            return self._obter_chave_cache() in cache.get("enviados", [])
        except Exception:
            return False

    def registrar_envio(self):
        from datetime import datetime
        from config.settings import settings
        import json
        
        hoje = datetime.now().strftime("%Y-%m-%d")
        cache_file = settings.APP_DIR / "config" / "envios_cache.json"
        chave = self._obter_chave_cache()
        try:
            if cache_file.exists():
                with open(cache_file, "r", encoding="utf-8") as f:
                    cache = json.load(f)
            else:
                cache = {"data": hoje, "enviados": []}
                
            if cache.get("data") != hoje:
                cache = {"data": hoje, "enviados": []}
                
            if chave not in cache["enviados"]:
                cache["enviados"].append(chave)
                
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(cache, f)
        except Exception:
            pass

    def pode_enviar_hoje(self) -> bool:
        """
        Verifica se a mensagem pode ser enviada no momento atual:
        1. Se mensagem_programada estiver vazia (guiado por data_máxima):
           - Envia nas 4 janelas padrão (08, 11, 14, 17).
           - Se tiver hora limite específica (ex: 10h em 09/10/2026), envia também às 10h.
        2. Se mensagem_programada estiver preenchida:
           - Envia a partir da data/hora exata programada.
        """
        dt_str = str(self.mensagem_programada or "").strip()
        from datetime import datetime
        agora = datetime.now()

        if not dt_str:
            # Automático (data_máxima): Janelas padrão (08, 11, 14, 17)
            hora_str = agora.strftime("%H")
            janelas_padrao = ["08", "11", "14", "17"]
            if hora_str in janelas_padrao:
                return True

            # Se houver hora limite personalizada em data_máxima (ex: 10h)
            hora_especifica = self.obter_hora_limite_data_maxima()
            if hora_especifica and hora_str == hora_especifica:
                return True

            return False

        import re
        clean_str = dt_str.lower().strip()

        # Normalizar "11h30" -> "11:30" e "11h" -> "11:00"
        clean_str = re.sub(r'(\d{1,2})\s*h\s*(\d{2})', r'\1:\2', clean_str)
        clean_str = re.sub(r'(\d{1,2})\s*h\b', r'\1:00', clean_str)

        try:
            # 1. Formatos Apenas com Hora (ex: 11:00, 11:00:00)
            for fmt in ("%H:%M", "%H:%M:%S"):
                try:
                    dt_parsed = datetime.strptime(clean_str, fmt)
                    dt_prog = datetime.combine(agora.date(), dt_parsed.time())
                    if agora >= dt_prog:
                        return True
                    return False
                except ValueError:
                    continue

            # 2. Formatos com Data e Hora (ex: 09/10/2026 10:00, 09/10/26 10:00)
            for fmt in (
                "%d/%m/%Y %H:%M", "%d/%m/%Y %H:%M:%S",
                "%d/%m/%y %H:%M", "%d/%m/%y %H:%M:%S",
                "%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"
            ):
                try:
                    dt_prog = datetime.strptime(clean_str, fmt)
                    if agora >= dt_prog:
                        return True
                    return False
                except ValueError:
                    continue

            # 3. Formatos apenas com Data (ex: 09/10/2026, 09/10/26)
            for fmt in ("%d/%m/%Y", "%d/%m/%y", "%Y-%m-%d"):
                try:
                    dt_prog = datetime.strptime(clean_str, fmt).date()
                    return dt_prog <= agora.date()
                except ValueError:
                    continue
        except Exception:
            pass

        return False # Se não der match em nada e tiver texto inválido, não envia

    def formatar_telefone_valido(self) -> str:
        from src.utils.formatters import formatar_telefone
        return formatar_telefone(self.telefone)

