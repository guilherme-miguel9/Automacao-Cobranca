import sys
import time
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QPlainTextEdit, QFrame
)
from PySide6.QtCore import Qt, QThread, Signal
from main import executar_ciclo, modo_agendado
from src.utils.logger import logger

class BotWorkerThread(QThread):
    log_signal = Signal(str)
    finished_signal = Signal()

    def __init__(self, mode="single"):
        super().__init__()
        self.mode = mode
        self.is_running = True

    def run(self):
        try:
            if self.mode == "single":
                executar_ciclo()
            elif self.mode == "loop":
                modo_agendado()
        except Exception as e:
            logger.error(f"Erro na execução do robô: {e}")
        finally:
            self.finished_signal.emit()

class ExecutionView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(20)

        # Glass Control Card
        card = QFrame()
        card.setObjectName("glassCard")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(24, 24, 24, 24)
        card_layout.setSpacing(16)

        title = QLabel("Painel de Controle e Disparo do Robô")
        title.setObjectName("sectionTitle")
        card_layout.addWidget(title)

        desc = QLabel("Inicie disparos manuais em tempo real ou ative o modo agendado contínuo.")
        desc.setObjectName("subText")
        card_layout.addWidget(desc)

        # Action Buttons
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(14)

        self.btn_run = QPushButton("Executar Ciclo de Cobranca")
        self.btn_run.setObjectName("primaryButton")
        self.btn_run.clicked.connect(self.start_single_run)

        self.btn_schedule = QPushButton("Iniciar Agendamento Automatico (Verifica a cada minuto)")
        self.btn_schedule.setObjectName("secondaryButton")
        self.btn_schedule.clicked.connect(self.start_loop_run)

        self.btn_stop = QPushButton("Interromper Execucao")
        self.btn_stop.setObjectName("secondaryButton")
        self.btn_stop.setEnabled(False)
        self.btn_stop.clicked.connect(self.stop_run)

        btn_layout.addWidget(self.btn_run)
        btn_layout.addWidget(self.btn_schedule)
        btn_layout.addWidget(self.btn_stop)

        card_layout.addLayout(btn_layout)

        # Live Terminal Log Output
        log_title = QLabel("Terminal de Logs em Tempo Real:")
        log_title.setObjectName("sectionTitle")
        card_layout.addWidget(log_title)

        self.log_terminal = QPlainTextEdit()
        self.log_terminal.setReadOnly(True)
        self.log_terminal.setStyleSheet(
            "background-color: #030712; "
            "color: #38BDF8; "
            "font-family: 'Consolas', 'Courier New', monospace; "
            "font-size: 12px; "
            "border: 1px solid rgba(56, 189, 248, 0.3); "
            "border-radius: 12px; "
            "padding: 12px;"
        )
        card_layout.addWidget(self.log_terminal)

        layout.addWidget(card)

        # Redirect Log Stream
        self.append_log("[INFO] Sistema pronto para iniciar execuções. Selecione uma ação acima.\n")

    def append_log(self, text: str):
        self.log_terminal.appendPlainText(text)

    def start_single_run(self):
        self.btn_run.setEnabled(False)
        self.btn_schedule.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.append_log("[INFO] Iniciando disparo de ciclo único em segundo plano...")

        self.worker = BotWorkerThread(mode="single")
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.start()

    def start_loop_run(self):
        self.btn_run.setEnabled(False)
        self.btn_schedule.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.append_log("[INFO] Modo Agendado Ativado (Verificacao a cada minuto)...")

        self.worker = BotWorkerThread(mode="loop")
        self.worker.finished_signal.connect(self.on_worker_finished)
        self.worker.start()

    def stop_run(self):
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.append_log("[AVISO] Execução interrompida pelo usuário.")
        self.on_worker_finished()

    def on_worker_finished(self):
        self.btn_run.setEnabled(True)
        self.btn_schedule.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.append_log("[SUCESSO] Ciclo finalizado.")
