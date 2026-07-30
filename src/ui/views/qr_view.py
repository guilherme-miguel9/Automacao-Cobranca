import io
import requests
import qrcode
from PIL import Image
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame, QScrollArea
)
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtGui import QPixmap, QImage
from config.settings import settings
from src.utils.logger import logger

class HealthCheckWorker(QThread):
    status_signal = Signal(bool, str)  # is_online, message

    def run(self):
        try:
            health_url = settings.WHATSAPP_API_URL.replace("/api/v1/send-message", "/health")
            res = requests.get(health_url, timeout=3)
            if res.status_code == 200:
                data = res.json()
                is_connected = data.get("connected", False)
                if is_connected:
                    self.status_signal.emit(True, "WhatsApp Conectado e Operacional")
                else:
                    self.status_signal.emit(False, "WhatsApp Desconectado. Escaneie o QR Code no Gateway.")
            else:
                self.status_signal.emit(False, f"Gateway offline (HTTP {res.status_code})")
        except Exception as e:
            self.status_signal.emit(False, f"Gateway local inacessível (Porta 8000)")

class QRView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Glass Container
        card = QFrame()
        card.setObjectName("glassCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(32, 32, 32, 32)
        card_layout.setSpacing(20)
        card_layout.setAlignment(Qt.AlignCenter)

        # Title & Description
        title = QLabel("Conexão do WhatsApp (Gateway Local)")
        title.setObjectName("sectionTitle")
        
        desc = QLabel(
            "Verifique o status do gateway gratuito local e leia o QR Code no seu celular "
            "para parear a conta de envio de notificações."
        )
        desc.setObjectName("subText")
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignCenter)

        # Status Badge
        self.status_badge = QLabel("Verificando Conexão...")
        self.status_badge.setObjectName("statusBadgeOffline")
        self.status_badge.setAlignment(Qt.AlignCenter)

        # QR Code Display Box
        self.qr_label = QLabel()
        self.qr_label.setFixedSize(260, 260)
        self.qr_label.setStyleSheet(
            "background-color: rgba(15, 23, 42, 0.9); "
            "border: 2px dashed rgba(56, 189, 248, 0.3); "
            "border-radius: 16px;"
        )
        self.qr_label.setAlignment(Qt.AlignCenter)

        # Buttons Layout
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_check = QPushButton("🔄 Verificar Conexão")
        self.btn_check.setObjectName("primaryButton")
        self.btn_check.clicked.connect(self.check_status)

        btn_layout.addWidget(self.btn_check)

        # Assembly
        card_layout.addWidget(title, alignment=Qt.AlignCenter)
        card_layout.addWidget(desc, alignment=Qt.AlignCenter)
        card_layout.addWidget(self.status_badge, alignment=Qt.AlignCenter)
        card_layout.addWidget(self.qr_label, alignment=Qt.AlignCenter)
        card_layout.addLayout(btn_layout)

        layout.addWidget(card)
        
        # Initial Check
        self.check_status()

    def check_status(self):
        self.status_badge.setText("Verificando Conexão com Gateway...")
        self.worker = HealthCheckWorker()
        self.worker.status_signal.connect(self.on_status_result)
        self.worker.start()

    def on_status_result(self, is_online: bool, message: str):
        if is_online:
            self.status_badge.setText("🟢 WHATSAPP CONECTADO E OPERACIONAL")
            self.status_badge.setObjectName("statusBadgeOnline")
            self.status_badge.setStyle(self.status_badge.style())
            self.show_connected_graphic()
        else:
            self.status_badge.setText(f"🔴 {message}")
            self.status_badge.setObjectName("statusBadgeOffline")
            self.status_badge.setStyle(self.status_badge.style())
            self.show_placeholder_qr()

    def show_connected_graphic(self):
        pixmap = QPixmap(240, 240)
        pixmap.fill(Qt.transparent)
        self.qr_label.setPixmap(pixmap)
        self.qr_label.setText("✅ WhatsApp Pronto\npara Enviar Notificações!")
        self.qr_label.setStyleSheet(
            "color: #34D399; font-size: 16px; font-weight: 700; "
            "background-color: rgba(16, 185, 129, 0.1); "
            "border: 2px solid rgba(52, 211, 153, 0.5); "
            "border-radius: 16px;"
        )

    def show_placeholder_qr(self):
        self.qr_label.setText("📱 Inicie o Gateway Node\npara ler o QR Code")
        self.qr_label.setStyleSheet(
            "color: #94A3B8; font-size: 13px; "
            "background-color: rgba(15, 23, 42, 0.9); "
            "border: 2px dashed rgba(56, 189, 248, 0.3); "
            "border-radius: 16px;"
        )
