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
        app_id = "qualidade.cobobrabot.openclaw.v1"
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
    app.setApplicationName("CobobraBot")
    app.setOrganizationName("Núcleo de Qualidade")

    # Tentar icon.ico (para Windows Taskbar/Titlebar) e fallback para icon.png
    icon_ico = get_asset_path("src/assets/icon.ico")
    icon_png = get_asset_path("src/assets/icon.png")
    
    icon_target = icon_ico if icon_ico.exists() else icon_png

    if icon_target.exists():
        app_icon = QIcon(str(icon_target))
        if icon_png.exists():
            app_icon.addFile(str(icon_png))
        app.setWindowIcon(app_icon)

    window = MainWindow()
    if icon_target.exists():
        win_icon = QIcon(str(icon_target))
        if icon_png.exists():
            win_icon.addFile(str(icon_png))
        window.setWindowIcon(win_icon)
        
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
