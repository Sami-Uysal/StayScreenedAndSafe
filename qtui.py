import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QVBoxLayout, QLabel, QLineEdit, \
    QPushButton, QTabWidget
from PyQt5.QtGui import QFont, QPalette, QColor
from two_factor_auth import generate_qr, verify_code

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StayScreenedAndSafe")
        self.setGeometry(100, 100, 800, 600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_2fa = QWidget()
        self.tab_face = QWidget()

        self.tabs.addTab(self.tab_2fa, "2FA Doğrulama")
        self.tabs.addTab(self.tab_face, "Yüz Tanıma")

        self.setup_2fa_tab()
        self.setup_face_tab()

        self.apply_styles()

    def setup_2fa_tab(self):
        layout = QVBoxLayout()

        self.username_label = QLabel("Kullanıcı Adı:")
        self.username_entry = QLineEdit()
        self.generate_button = QPushButton("QR Kod Oluştur/Göster")
        self.qr_label = QLabel()
        self.code_label = QLabel("2FA Kodu:")
        self.code_entry = QLineEdit()
        self.verify_button = QPushButton("Kodu Doğrula")

        self.generate_button.clicked.connect(self.generate_qr)
        self.verify_button.clicked.connect(self.verify_code)

        layout.addWidget(self.username_label)
        layout.addWidget(self.username_entry)
        layout.addWidget(self.generate_button)
        layout.addWidget(self.qr_label)
        layout.addWidget(self.code_label)
        layout.addWidget(self.code_entry)
        layout.addWidget(self.verify_button)

        self.tab_2fa.setLayout(layout)

    def setup_face_tab(self):
        layout = QVBoxLayout()

        self.face_register_button = QPushButton("Yüz Kayıt")
        self.face_verify_button = QPushButton("Yüz Doğrulama")

        self.face_register_button.clicked.connect(self.face_register)
        self.face_verify_button.clicked.connect(self.face_verify)

        layout.addWidget(self.face_register_button)
        layout.addWidget(self.face_verify_button)

        self.tab_face.setLayout(layout)

    def generate_qr(self):
        username = self.username_entry.text()
        message = generate_qr(username, self.qr_label)
        QMessageBox.information(self, "Bilgi", message)

    def verify_code(self):
        username = self.username_entry.text()
        code = self.code_entry.text()
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
            QMainWindow {
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
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
