# This Python file uses the following encoding: utf-8
import sys
from PySide6.QtWidgets import QApplication, QWidget, QMessageBox
from ui_form import Ui_Widget
from two_factor_auth import generate_qr, verify_code


class Widget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Widget()
        self.ui.setupUi(self)

        # Connect buttons to functions
        self.ui.generate_button.clicked.connect(self.generate_qr)
        self.ui.verify_button.clicked.connect(self.verify_code)
        self.ui.face_register_button.clicked.connect(self.face_register)
        self.ui.face_verify_button.clicked.connect(self.face_verify)

        # Apply styles
        self.apply_styles()

    def generate_qr(self):
        username = self.ui.username_entry.text()
        message = generate_qr(username, self.ui.qr_label)
        QMessageBox.information(self, "Bilgi", message)

    def verify_code(self):
        username = self.ui.username_entry.text()
        code = self.ui.code_entry.text()
        success, message = verify_code(username, code)
        if success:
            QMessageBox.information(self, "Başarılı", message)
        else:
            QMessageBox.warning(self, "Hata", message)

    def face_register(self):
        QMessageBox.information(self, "Bilgi", "Yüzünüz başarıyla kaydedildi")

    def face_verify(self):
        QMessageBox.information(self, "Bilgi", "Yüz doğrulama işlemi başlatıldı")

    def apply_styles(self):
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
            }
            QLabel {
                font-size: 16px;
                color: #333333;
            }
            QLineEdit {
                font-size: 14px;
                padding: 5px;
                border: 1px solid #cccccc;
                border-radius: 5px;
            }
            QPushButton {
                font-size: 14px;
                padding: 10px;
                border: 1px solid #0078d7;
                border-radius: 5px;
                background-color: #0078d7;
                color: #ffffff;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
            QTabWidget::pane {
                border: 1px solid #cccccc;
            }
            QTabBar::tab {
                background: #e0e0e0;
                padding: 10px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-bottom: 2px solid #0078d7;
            }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = Widget()
    widget.show()
    sys.exit(app.exec())
