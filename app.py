import sys
import ctypes
from pathlib import Path
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from src.ui.main_window import MainWindow

# Forçar o Windows a tratar o app com ID próprio para exibir o ícone correto na barra de tarefas/título
if sys.platform == "win32":
    try:
        app_id = "qualidade.cobrabot.v1"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass

def get_asset_path(relative_path: str) -> Path:
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent
    return base / relative_path

def main():
    # Enable High DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    
    app = QApplication(sys.argv)
    app.setApplicationName("Cobra Bot")
    app.setOrganizationName("Núcleo de Qualidade")

    # Tentar icon.png e fallback para icon.ico
    icon_png = get_asset_path("src/assets/icon.png")
    icon_ico = get_asset_path("src/assets/icon.ico")
    
    icon_target = icon_png if icon_png.exists() else icon_ico

    if icon_target.exists():
        app_icon = QIcon(str(icon_target))
        app.setWindowIcon(app_icon)

    window = MainWindow()
    if icon_target.exists():
        window.setWindowIcon(QIcon(str(icon_target)))
        
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
