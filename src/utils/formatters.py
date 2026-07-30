import re

def formatar_moeda(valor: float) -> str:
    """
    Formatador para exibição em formato de Moeda Brasileira (R$).
    """
    try:
        return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return f"R$ {valor}"

def formatar_telefone(telefone: str) -> str:
    """
    Formatador de números de telefone para o padrão WhatsApp internacional (+55...).
    Permite Links de Grupo (chat.whatsapp.com) ou IDs Diretos (@g.us)
    """
    if not telefone:
        return ""
    
    tel_str = str(telefone).strip()
    
    # Se for um grupo ou link de convite, mantém o texto original
    if "chat.whatsapp.com" in tel_str or "@g.us" in tel_str:
        return tel_str
        
    # Remover caracteres não numéricos
    apenas_numeros = re.sub(r"\D", "", tel_str)
    
    # Adicionar DDI 55 caso não tenha
    if len(apenas_numeros) in (10, 11) and not apenas_numeros.startswith("55"):
        apenas_numeros = f"55{apenas_numeros}"
        
    return apenas_numeros

def formatar_data_limpa(data_str: str) -> str:
    """
    Remove '00:00:00' e ajusta formato de data para exibição amigável.
    """
    if not data_str:
        return ""
    data_clean = str(data_str).strip()
    return data_clean.replace(" 00:00:00", "").replace(" 00:00", "")

def formatar_mensagem_pendencia(nome_solicitante: str, pendencia_id: str, descricao: str, data_maxima: str, hora_limite: str = "", valor: float = 0.0, codigo_barras: str = "", mensagem_programada: str = "") -> str:
    """
    Gera a mensagem padronizada do WhatsApp para aviso de pendência.
    """
    data_exibicao = formatar_data_limpa(data_maxima)
    is_agendado_sem_data = bool(mensagem_programada and not data_maxima)
    
    msg = (
        f"Olá, *{nome_solicitante}*!\n"
        f"Sou o assistente virtual do Núcleo de Qualidade.\n\n"
    )
    
    if is_agendado_sem_data:
        msg += (
            f"Notificação referente a: *{pendencia_id}*.\n\n"
            f"*Detalhes:*\n"
        )
    else:
        msg += (
            f"Notificação referente à pendência *{pendencia_id}*.\n\n"
            f"*Detalhes da Pendência:*\n"
        )
        
    msg += f"• *Descrição:* {descricao}\n"
    
    if not is_agendado_sem_data:
        msg += f"• *Prazo Máximo:* {data_exibicao}\n"
        if hora_limite:
            msg += f"• *Hora Limite:* {hora_limite}\n"
    
    if valor and valor > 0:
        msg += f"• *Valor:* {formatar_moeda(valor)}\n"

    if codigo_barras:
        msg += f"\n*Código de Barras / Chave PIX:*\n`{codigo_barras}`\n"
        
    if not is_agendado_sem_data:
        msg += "\nFavor verificar o andamento ou responder a esta mensagem em caso de dúvidas.\n"

    msg += "\nAtenciosamente,\n*Equipe do Núcleo de Qualidade*"
    
    return msg

def formatar_mensagem_cobranca(nome: str, uc: str, valor: float, vencimento: str, codigo_barras: str = "") -> str:
    return formatar_mensagem_pendencia(
        nome_solicitante=nome,
        pendencia_id=uc,
        descricao="Pendência de Débito em Aberto",
        data_maxima=vencimento,
        valor=valor,
        codigo_barras=codigo_barras
    )
