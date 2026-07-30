import os
from pathlib import Path
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
        card_layout.setSpacing(18)

        # Title
        title = QLabel("Configurações do Sistema e Arquivo .env")
        title.setObjectName("sectionTitle")
        card_layout.addWidget(title)

        desc = QLabel("Altere a planilha do Google Sheets, modo de teste e diretório dos relatórios de auditoria.")
        desc.setObjectName("subText")
        card_layout.addWidget(desc)

        # 1. Google Sheet URL / Name
        lbl_sheet = QLabel("Link ou Nome da Planilha no Google Sheets:")
        self.input_sheet = QLineEdit()
        self.input_sheet.setText(settings.GSHEET_SPREADSHEET_NAME)
        self.input_sheet.setPlaceholderText("https://docs.google.com/spreadsheets/d/...")
        card_layout.addWidget(lbl_sheet)
        card_layout.addWidget(self.input_sheet)

        # 2. Output Report Directory Selector
        lbl_output = QLabel("Local de Armazenamento dos Relatórios em CSV:")
        out_layout = QHBoxLayout()
        self.input_output_dir = QLineEdit()
        self.input_output_dir.setText(str(settings.OUTPUT_DIR.resolve()))
        btn_browse = QPushButton("📁 Escolher Pasta...")
        btn_browse.setObjectName("secondaryButton")
        btn_browse.clicked.connect(self.browse_output_dir)
        out_layout.addWidget(self.input_output_dir)
        out_layout.addWidget(btn_browse)
        card_layout.addWidget(lbl_output)
        card_layout.addLayout(out_layout)

        # 3. WhatsApp Gateway API URL
        lbl_gw = QLabel("URL do Gateway Local do WhatsApp:")
        self.input_gw_url = QLineEdit()
        self.input_gw_url.setText(settings.WHATSAPP_API_URL)
        card_layout.addWidget(lbl_gw)
        card_layout.addWidget(self.input_gw_url)

        # 4. Dry Run Mode
        self.chk_dry_run = QCheckBox("Modo Simulação (DRY_RUN - Não dispara WhatsApp de verdade)")
        self.chk_dry_run.setChecked(settings.DRY_RUN)
        self.chk_dry_run.setStyleSheet("font-size: 13px; font-weight: 600; color: #F8FAFC;")
        card_layout.addWidget(self.chk_dry_run)

        # 5. Locked Google Credentials (NOT editable as requested by user)
        lbl_creds = QLabel("🔒 Credenciais do Google Cloud (google_credentials.json) - [Bloqueado / Não Editável]:")
        self.input_creds = QLineEdit()
        self.input_creds.setText(str(settings.GOOGLE_CREDENTIALS_FILE))
        self.input_creds.setReadOnly(True)
        card_layout.addWidget(lbl_creds)
        card_layout.addWidget(self.input_creds)

        # Save Button
        btn_save = QPushButton("💾 Salvar Alterações no .env")
        btn_save.setObjectName("primaryButton")
        btn_save.clicked.connect(self.save_settings)
        card_layout.addWidget(btn_save, alignment=Qt.AlignRight)

        layout.addWidget(card)

    def browse_output_dir(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione o diretório para relatórios em CSV", str(settings.OUTPUT_DIR))
        if folder:
            self.input_output_dir.setText(folder)

    def save_settings(self):
        try:
            env_file = settings.BASE_DIR / "config" / ".env"
            sheet_val = self.input_sheet.text().strip()
            out_val = self.input_output_dir.text().strip()
            gw_val = self.input_gw_url.text().strip()
            dry_val = "True" if self.chk_dry_run.isChecked() else "False"

            # Atualizar arquivo .env
            lines = [
                f"GSHEET_SPREADSHEET_NAME={sheet_val}\n",
                f"DRY_RUN={dry_val}\n",
                f"WHATSAPP_API_URL={gw_val}\n",
                f"OUTPUT_DIR={out_val}\n"
            ]

            with open(env_file, "w", encoding="utf-8") as f:
                f.writelines(lines)

            # Atualizar memória do settings
            settings.GSHEET_SPREADSHEET_NAME = sheet_val
            settings.DRY_RUN = (dry_val == "True")
            settings.WHATSAPP_API_URL = gw_val
            settings.OUTPUT_DIR = Path(out_val)
            settings.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

            QMessageBox.information(self, "Sucesso", "Configurações salvas com sucesso no arquivo .env!")
        except Exception as e:
            QMessageBox.critical(self, "Erro ao Salvar", f"Não foi possível salvar o arquivo .env: {e}")
