from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QPushButton, 
    QStackedWidget, QLabel, QFrame
)
from pathlib import Path
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
from src.ui.styles import GLASS_STYLE
from src.ui.views.execution_view import ExecutionView
from src.ui.views.qr_view import QRView
from src.ui.views.settings_view import SettingsView
from src.ui.views.template_view import TemplateView
from config.settings import settings

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Automação de Cobranças - OpenClaw Bot")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)
        self.setStyleSheet(GLASS_STYLE)

        self.init_ui()

    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Left Sidebar
        sidebar = QFrame()
        sidebar.setObjectName("sidebarFrame")
        sidebar.setFixedWidth(240)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(16, 24, 16, 24)
        sidebar_layout.setSpacing(12)

        # App Brand Title with Logo Icon
        brand_container = QHBoxLayout()
        brand_container.setSpacing(12)

        icon_label = QLabel()
        import sys
        if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
            icon_path = Path(sys._MEIPASS) / "src" / "assets" / "icon.png"
        else:
            icon_path = settings.BASE_DIR / "src" / "assets" / "icon.png"

        if icon_path.exists():
            pixmap = QPixmap(str(icon_path)).scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)

        brand_text_layout = QVBoxLayout()
        brand_text_layout.setSpacing(2)

        brand_label = QLabel("CobrançaBot")
        brand_label.setObjectName("headerTitle")
        sub_brand = QLabel("Núcleo de Qualidade")
        sub_brand.setObjectName("subText")

        brand_text_layout.addWidget(brand_label)
        brand_text_layout.addWidget(sub_brand)

        brand_container.addWidget(icon_label)
        brand_container.addLayout(brand_text_layout)

        sidebar_layout.addLayout(brand_container)
        sidebar_layout.addSpacing(20)

        # Navigation Buttons
        self.btn_nav_exec = QPushButton("Disparos e Logs")
        self.btn_nav_exec.setObjectName("navButton")
        self.btn_nav_exec.setProperty("active", True)
        self.btn_nav_exec.clicked.connect(lambda: self.switch_tab(0, self.btn_nav_exec))

        self.btn_nav_qr = QPushButton("WhatsApp e QR Code")
        self.btn_nav_qr.setObjectName("navButton")
        self.btn_nav_qr.clicked.connect(lambda: self.switch_tab(1, self.btn_nav_qr))

        self.btn_nav_settings = QPushButton("Configuracoes (.env)")
        self.btn_nav_settings.setObjectName("navButton")
        self.btn_nav_settings.clicked.connect(lambda: self.switch_tab(2, self.btn_nav_settings))

        self.btn_nav_template = QPushButton("Template de Mensagem")
        self.btn_nav_template.setObjectName("navButton")
        self.btn_nav_template.clicked.connect(lambda: self.switch_tab(3, self.btn_nav_template))

        sidebar_layout.addWidget(self.btn_nav_exec)
        sidebar_layout.addWidget(self.btn_nav_qr)
        sidebar_layout.addWidget(self.btn_nav_settings)
        sidebar_layout.addWidget(self.btn_nav_template)
        sidebar_layout.addStretch()

        # Version & Mode Info
        mode_str = "Modo: DRY_RUN (Simulação)" if settings.DRY_RUN else "Modo: REAL (Produção)"
        lbl_mode = QLabel(mode_str)
        lbl_mode.setObjectName("subText")
        sidebar_layout.addWidget(lbl_mode)

        # 2. Right Content Area (Stacked Widget)
        content_area = QWidget()
        content_layout = QVBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)

        # Header Bar
        header = QFrame()
        header.setStyleSheet("background-color: rgba(15, 23, 42, 0.5); border-bottom: 1px solid rgba(255, 255, 255, 0.08);")
        header.setFixedHeight(60)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 0, 24, 0)

        self.header_title = QLabel("Painel Principal de Disparos")
        self.header_title.setObjectName("sectionTitle")

        header_layout.addWidget(self.header_title)
        header_layout.addStretch()

        content_layout.addWidget(header)

        # Stacked Pages
        self.stack = QStackedWidget()
        self.view_exec = ExecutionView()
        self.view_qr = QRView()
        self.view_settings = SettingsView()
        self.view_template = TemplateView()

        self.stack.addWidget(self.view_exec)
        self.stack.addWidget(self.view_qr)
        self.stack.addWidget(self.view_settings)
        self.stack.addWidget(self.view_template)

        content_layout.addWidget(self.stack)

        main_layout.addWidget(sidebar)
        main_layout.addWidget(content_area)

        self.nav_buttons = [self.btn_nav_exec, self.btn_nav_qr, self.btn_nav_settings, self.btn_nav_template]

    def switch_tab(self, index: int, active_btn: QPushButton):
        self.stack.setCurrentIndex(index)
        titles = [
            "Painel Principal de Disparos",
            "Conexao do WhatsApp e QR Code",
            "Configuracoes Globais e Variaveis .env",
            "Editor de Modelo de Mensagem"
        ]
        self.header_title.setText(titles[index])

        for btn in self.nav_buttons:
            btn.setProperty("active", btn == active_btn)
            btn.setStyle(btn.style())
