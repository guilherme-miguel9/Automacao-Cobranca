from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, 
    QPushButton, QFrame, QMessageBox
)
from PySide6.QtCore import Qt
from src.utils.formatters import formatar_mensagem_pendencia

DEFAULT_TEMPLATE = (
    "Olá, *{nome_solicitante}*! 👋\n"
    "Sou o assistente virtual do Núcleo de Qualidade.\n\n"
    "Notificação referente à pendência *{pendencia_id}*.\n\n"
    "📌 *Detalhes da Pendência:*\n"
    "• *Descrição:* {descricao}\n"
    "• *Prazo Máximo:* {prazo_maximo}\n"
    "• *Hora Limite:* {hora_limite}\n\n"
    "Favor verificar o andamento ou responder a esta mensagem em caso de dúvidas.\n\n"
    "Atenciosamente,\n"
    "*Equipe do Núcleo de Qualidade*"
)

class TemplateView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Left Column: Editor Card
        left_card = QFrame()
        left_card.setObjectName("glassCard")
        left_layout = QVBoxLayout(left_card)
        left_layout.setContentsMargins(24, 24, 24, 24)
        left_layout.setSpacing(14)

        title = QLabel("Editor da Mensagem Padrão de WhatsApp")
        title.setObjectName("sectionTitle")
        left_layout.addWidget(title)

        desc = QLabel("Personalize o texto da notificação enviado aos contatos. Use as variáveis abaixo.")
        desc.setObjectName("subText")
        left_layout.addWidget(desc)

        # Variables helper buttons
        vars_layout = QHBoxLayout()
        vars_layout.setSpacing(8)
        
        btn_v1 = QPushButton("{nome_solicitante}")
        btn_v1.setObjectName("secondaryButton")
        btn_v1.clicked.connect(lambda: self.insert_var("{nome_solicitante}"))

        btn_v2 = QPushButton("{pendencia_id}")
        btn_v2.setObjectName("secondaryButton")
        btn_v2.clicked.connect(lambda: self.insert_var("{pendencia_id}"))

        btn_v3 = QPushButton("{descricao}")
        btn_v3.setObjectName("secondaryButton")
        btn_v3.clicked.connect(lambda: self.insert_var("{descricao}"))

        btn_v4 = QPushButton("{prazo_maximo}")
        btn_v4.setObjectName("secondaryButton")
        btn_v4.clicked.connect(lambda: self.insert_var("{prazo_maximo}"))

        vars_layout.addWidget(btn_v1)
        vars_layout.addWidget(btn_v2)
        vars_layout.addWidget(btn_v3)
        vars_layout.addWidget(btn_v4)

        left_layout.addLayout(vars_layout)

        # Text Editor
        self.txt_editor = QTextEdit()
        self.txt_editor.setPlainText(DEFAULT_TEMPLATE)
        self.txt_editor.textChanged.connect(self.update_preview)
        left_layout.addWidget(self.txt_editor)

        # Right Column: Live Preview Card
        right_card = QFrame()
        right_card.setObjectName("glassCard")
        right_layout = QVBoxLayout(right_card)
        right_layout.setContentsMargins(24, 24, 24, 24)
        right_layout.setSpacing(14)

        prev_title = QLabel("📱 Pré-visualização no WhatsApp")
        prev_title.setObjectName("sectionTitle")
        right_layout.addWidget(prev_title)

        self.preview_box = QTextEdit()
        self.preview_box.setReadOnly(True)
        self.preview_box.setStyleSheet(
            "background-color: rgba(15, 23, 42, 0.95); "
            "border: 1px solid rgba(56, 189, 248, 0.3); "
            "border-radius: 12px; color: #E2E8F0; padding: 14px;"
        )
        right_layout.addWidget(self.preview_box)

        layout.addWidget(left_card, stretch=3)
        layout.addWidget(right_card, stretch=2)

        self.update_preview()

    def insert_var(self, var_name: str):
        self.txt_editor.insertPlainText(var_name)

    def update_preview(self):
        text = self.txt_editor.toPlainText()
        preview = text.format(
            nome_solicitante="GUILHERME",
            pendencia_id="PEND-102",
            descricao="Ajuste no medidor da quadra B",
            prazo_maximo="30/07/2026",
            hora_limite="17:00"
        )
        self.preview_box.setPlainText(preview)
