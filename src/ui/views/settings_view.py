import os
from pathlib import Path
from dotenv import load_dotenv
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QCheckBox, QFrame, QFileDialog, QMessageBox
)
from PySide6.QtCore import Qt
from config.settings import settings

class SettingsView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Glass Card
        card = QFrame()
        card.setObjectName("glassCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(28, 28, 28, 28)
        card_layout.setSpacing(22)

        # Title
        title = QLabel("Configuracoes de Armazenamento e Execucao")
        title.setObjectName("sectionTitle")
        card_layout.addWidget(title)

        desc = QLabel("Defina a pasta local onde os relatorios consolidado de cobranca em CSV serao salvos e ajuste o modo de execucao.")
        desc.setObjectName("subText")
        card_layout.addWidget(desc)

        # 1. Output Report Directory Selector
        lbl_output = QLabel("Local de Armazenamento dos Relatorios (CSV):")
        out_layout = QHBoxLayout()
        self.input_output_dir = QLineEdit()
        self.input_output_dir.setText(str(settings.OUTPUT_DIR.resolve()))
        btn_browse = QPushButton("Selecionar Pasta...")
        btn_browse.setObjectName("secondaryButton")
        btn_browse.clicked.connect(self.browse_output_dir)
        out_layout.addWidget(self.input_output_dir)
        out_layout.addWidget(btn_browse)
        card_layout.addWidget(lbl_output)
        card_layout.addLayout(out_layout)

        # 2. Dry Run Mode
        self.chk_dry_run = QCheckBox("Modo Simulacao (DRY_RUN - Nao dispara WhatsApp real)")
        self.chk_dry_run.setChecked(settings.DRY_RUN)
        self.chk_dry_run.setStyleSheet("font-size: 13px; font-weight: 600; color: #F8FAFC;")
        card_layout.addWidget(self.chk_dry_run)

        # Save Button
        btn_save = QPushButton("Salvar Alteracoes no .env")
        btn_save.setObjectName("primaryButton")
        btn_save.clicked.connect(self.save_settings)
        card_layout.addWidget(btn_save, alignment=Qt.AlignRight)

        layout.addWidget(card)
        layout.addStretch()

    def browse_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione a pasta para relatorios em CSV", str(settings.OUTPUT_DIR))
        if folder:
            self.input_output_dir.setText(folder)

    def save_settings(self):
        try:
            # 1. Obter valores
            dry_val = str(self.chk_dry_run.isChecked())
            out_val = self.input_output_dir.text().strip()

            # 2. Criar diretório config no APP_DIR se não existir
            env_dir = settings.APP_DIR / "config"
            env_dir.mkdir(parents=True, exist_ok=True)
            env_file = env_dir / ".env"

            # 3. Reescrever o .env com as chaves customizadas
            # Preservar chaves padrão fixas do sistema no .env
            lines = [
                f"GSHEET_SPREADSHEET_NAME={settings.GSHEET_SPREADSHEET_NAME}\n",
                f"GOOGLE_CREDENTIALS_FILE=config/google_credentials.json\n",
                f"WHATSAPP_API_URL={settings.WHATSAPP_API_URL}\n",
                f"DRY_RUN={dry_val}\n",
                f"OUTPUT_DIR={out_val}\n"
            ]

            with open(env_file, "w", encoding="utf-8") as f:
                f.writelines(lines)

            # Recarregar variáveis de ambiente em tempo de execução
            load_dotenv(env_file, override=True)

            # Atualizar memória do objeto settings
            settings.DRY_RUN = (dry_val == "True")
            settings.OUTPUT_DIR = Path(out_val)
            settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            QMessageBox.information(self, "Sucesso", f"Configurações salvas com sucesso no arquivo .env!\n\nModo DRY_RUN: {settings.DRY_RUN}")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Salvar", f"Não foi possível salvar o arquivo .env: {e}")
