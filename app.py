import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from src.ui.main_window import MainWindow

def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("CobrançaBot OpenClaw")
    app.setOrganizationName("Núcleo de Qualidade")

    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
