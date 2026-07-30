"""
Design System - Liquid Glass / Glassmorphism Style for PySide6 Desktop GUI.
"""

GLASS_STYLE = """
/* Base Window & Global Fonts */
QMainWindow {
    background-color: #090D16;
    color: #F8FAFC;
    font-family: 'Segoe UI', 'Inter', -apple-system, sans-serif;
}

QWidget {
    font-family: 'Segoe UI', 'Inter', sans-serif;
    color: #E2E8F0;
}

/* Frosted Glass Cards & Containers */
QFrame#glassCard, QWidget#glassCard {
    background-color: rgba(30, 41, 59, 0.65);
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 16px;
}

QFrame#sidebarFrame {
    background-color: rgba(15, 23, 42, 0.85);
    border-right: 1px solid rgba(255, 255, 255, 0.08);
}

/* Sidebar Navigation Buttons */
QPushButton#navButton {
    background-color: transparent;
    border: 1px solid transparent;
    border-radius: 12px;
    color: #94A3B8;
    padding: 12px 18px;
    font-size: 14px;
    font-weight: 600;
    text-align: left;
}

QPushButton#navButton:hover {
    background-color: rgba(56, 189, 248, 0.12);
    color: #38BDF8;
    border: 1px solid rgba(56, 189, 248, 0.25);
}

QPushButton#navButton:checked, QPushButton#navButton[active="true"] {
    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(6, 182, 212, 0.3), stop:1 rgba(99, 102, 241, 0.3));
    color: #FFFFFF;
    border: 1px solid rgba(56, 189, 248, 0.5);
    font-weight: 700;
}

/* Glass Action Buttons */
QPushButton#primaryButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #06B6D4, stop:1 #6366F1);
    color: #FFFFFF;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-size: 14px;
    font-weight: 700;
}

QPushButton#primaryButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #22D3EE, stop:1 #818CF8);
}

QPushButton#primaryButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #0891B2, stop:1 #4F46E5);
}

QPushButton#secondaryButton {
    background-color: rgba(51, 65, 85, 0.6);
    border: 1px solid rgba(255, 255, 255, 0.15);
    color: #F1F5F9;
    border-radius: 12px;
    padding: 10px 20px;
    font-size: 13px;
    font-weight: 600;
}

QPushButton#secondaryButton:hover {
    background-color: rgba(71, 85, 105, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.3);
}

/* Form Controls - Inputs & Text Areas */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.15);
    border-radius: 10px;
    padding: 10px 14px;
    color: #F8FAFC;
    selection-background-color: #06B6D4;
    font-size: 13px;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 1px solid #38BDF8;
    background-color: rgba(15, 23, 42, 0.9);
}

QLineEdit[readOnly="true"] {
    background-color: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    color: #64748B;
}

/* Labels & Headers */
QLabel#headerTitle {
    font-size: 22px;
    font-weight: 800;
    color: #F8FAFC;
}

QLabel#sectionTitle {
    font-size: 16px;
    font-weight: 700;
    color: #38BDF8;
}

QLabel#subText {
    font-size: 12px;
    color: #94A3B8;
}

/* Status Badges */
QLabel#statusBadgeOnline {
    background-color: rgba(16, 185, 129, 0.2);
    color: #34D399;
    border: 1px solid rgba(52, 211, 153, 0.4);
    border-radius: 8px;
    padding: 4px 10px;
    font-weight: 700;
    font-size: 12px;
}

QLabel#statusBadgeOffline {
    background-color: rgba(239, 68, 68, 0.2);
    color: #F87171;
    border: 1px solid rgba(248, 113, 113, 0.4);
    border-radius: 8px;
    padding: 4px 10px;
    font-weight: 700;
    font-size: 12px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: rgba(15, 23, 42, 0.5);
    width: 8px;
    border-radius: 4px;
}

QScrollBar::handle:vertical {
    background: rgba(148, 163, 184, 0.4);
    border-radius: 4px;
}

QScrollBar::handle:vertical:hover {
    background: rgba(56, 189, 248, 0.6);
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}
"""
