import sys
import pyotp
from mysql.connector import Error
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, \
    QLineEdit, QPushButton, QStackedWidget
from PyQt5.QtCore import Qt
from two_factor_auth import generate_qr_code, display_qr, verify_code, save_secret_key
import mysqlconnect

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("StayScreenedAndSafe")
        self.setGeometry(100, 100, 800, 600)

        # MySQL bağlantısını oluştur
        self.connection = mysqlconnect.create_connection()
        if self.connection is None:
            QMessageBox.critical(self, "Bağlantı Hatası", "MySQL veritabanına bağlanılamadı.")
            sys.exit(1)

        main_layout = QVBoxLayout()

        # Logo ekle
        self.logo_label = QLabel()
        self.logo_label.setPixmap(QPixmap("sssLogo.png").scaled(400, 200, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)

        self.stacked_widget = QStackedWidget()

        main_layout.addWidget(self.logo_label)
        main_layout.addWidget(self.stacked_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.setup_login_tab()
        self.setup_register_tab()
        self.setup_2fa_tab()
        self.setup_face_tab()

        self.apply_styles()

    def setup_login_tab(self):
        self.login_widget = QWidget()
        layout = QVBoxLayout()

        user_layout = QHBoxLayout()
        self.login_username_label = QLabel("Kullanıcı Adı:")
        self.login_username_entry = QLineEdit()
        user_layout.addWidget(self.login_username_label)
        user_layout.addWidget(self.login_username_entry)

        pass_layout = QHBoxLayout()
        self.login_password_label = QLabel("Parola:")
        self.login_password_entry = QLineEdit()
        self.login_password_entry.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(self.login_password_label)
        pass_layout.addWidget(self.login_password_entry)

        button_layout = QHBoxLayout()
        self.login_button = QPushButton("Giriş Yap")
        self.login_button.clicked.connect(self.login)
        self.go_to_register_button = QPushButton("Kayıt Ol")
        self.go_to_register_button.clicked.connect(self.show_register_tab)
        button_layout.addWidget(self.login_button)
        button_layout.addWidget(self.go_to_register_button)

        layout.addLayout(user_layout)
        layout.addLayout(pass_layout)
        layout.addLayout(button_layout)

        self.center_widgets(layout)
        self.login_widget.setLayout(layout)
        self.stacked_widget.addWidget(self.login_widget)

    def setup_register_tab(self):
        self.register_widget = QWidget()
        layout = QVBoxLayout()

        user_layout = QHBoxLayout()
        self.register_username_label = QLabel("Kullanıcı Adı:")
        self.register_username_entry = QLineEdit()
        user_layout.addWidget(self.register_username_label)
        user_layout.addWidget(self.register_username_entry)

        email_layout = QHBoxLayout()
        self.register_email_label = QLabel("Email:")
        self.register_email_entry = QLineEdit()
        email_layout.addWidget(self.register_email_label)
        email_layout.addWidget(self.register_email_entry)

        pass_layout = QHBoxLayout()
        self.register_password_label = QLabel("Parola:")
        self.register_password_entry = QLineEdit()
        self.register_password_entry.setEchoMode(QLineEdit.Password)
        pass_layout.addWidget(self.register_password_label)
        pass_layout.addWidget(self.register_password_entry)

        button_layout = QHBoxLayout()
        self.register_button = QPushButton("Kayıt Ol")
        self.register_button.clicked.connect(self.register)
        self.go_to_login_button = QPushButton("Giriş Yap")
        self.go_to_login_button.clicked.connect(self.show_login_tab)
        button_layout.addWidget(self.register_button)
        button_layout.addWidget(self.go_to_login_button)

        layout.addLayout(user_layout)
        layout.addLayout(email_layout)
        layout.addLayout(pass_layout)
        layout.addLayout(button_layout)

        self.center_widgets(layout)
        self.register_widget.setLayout(layout)
        self.stacked_widget.addWidget(self.register_widget)

    def setup_2fa_tab(self):
        self.tab_2fa = QWidget()
        layout = QVBoxLayout()

        self.qr_label_2fa = QLabel()
        self.qr_label_2fa.setAlignment(Qt.AlignCenter)  # Ortala

        code_layout = QHBoxLayout()
        self.code_label = QLabel("2FA Kodu:")
        self.code_entry = QLineEdit()
        code_layout.addWidget(self.code_label)
        code_layout.addWidget(self.code_entry)

        button_layout = QHBoxLayout()
        self.generate_button = QPushButton("QR Kod Oluştur/Göster")
        self.generate_button.clicked.connect(self.generate_qr)
        self.verify_button = QPushButton("Kodu Doğrula")
        self.verify_button.clicked.connect(self.verify_code)
        button_layout.addWidget(self.generate_button)
        button_layout.addWidget(self.verify_button)

        layout.addWidget(self.qr_label_2fa)
        layout.addLayout(code_layout)
        layout.addLayout(button_layout)

        self.center_widgets(layout)
        self.tab_2fa.setLayout(layout)
        self.stacked_widget.addWidget(self.tab_2fa)

    def setup_face_tab(self):
        self.tab_face = QWidget()
        layout = QVBoxLayout()

        self.face_register_button = QPushButton("Yüz Kayıt")
        self.face_register_button.clicked.connect(self.face_register)

        self.face_verify_button = QPushButton("Yüz Doğrulama")
        self.face_verify_button.clicked.connect(self.face_verify)

        layout.addWidget(self.face_register_button)
        layout.addWidget(self.face_verify_button)

        self.center_widgets(layout)
        self.tab_face.setLayout(layout)
        self.stacked_widget.addWidget(self.tab_face)

    def register(self):
        username = self.register_username_entry.text()
        email = self.register_email_entry.text()
        password = self.register_password_entry.text()

        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, password, email))
            self.connection.commit()
            QMessageBox.information(self, "Kayıt Başarılı", f"Kullanıcı {username} başarıyla kaydedildi!")
            self.stacked_widget.setCurrentWidget(self.login_widget)
            cursor.close()

        except Error as e:
            QMessageBox.warning(self, "Veritabanı Hatası", f"Hata: {e}")

    def login(self):
        username = self.login_username_entry.text()
        password = self.login_password_entry.text()
        self.logged_in_username = username  # Kullanıcı adını burada saklayın

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, password))
            user = cursor.fetchone()

            if user:
                QMessageBox.information(self, "Giriş Başarılı", "Başarıyla giriş yaptınız!")
                cursor.execute("SELECT * FROM two_factor_data WHERE user_id = %s", (user[0],))
                two_fa_data = cursor.fetchone()

                if not two_fa_data:
                    key = pyotp.random_base32()
                    save_secret_key(username, key)
                    generate_qr_code(username)
                display_qr(username, self.qr_label_2fa)
                self.stacked_widget.setCurrentWidget(self.tab_2fa)
            else:
                QMessageBox.warning(self, "Giriş Başarısız", "Kullanıcı adı veya parola yanlış!")

            cursor.close()

        except Error as e:
            QMessageBox.warning(self, "Veritabanı Hatası", f"Hata: {e}")

    def generate_qr(self):
        username = self.logged_in_username  # Giriş yapan kullanıcı adını kullanın
        display_qr(username, self.qr_label_2fa)

    def verify_code(self):
        username = self.logged_in_username  # Giriş yapan kullanıcı adını kullanın
        code = self.code_entry.text()
        success, message = verify_code(username, code)
        if success:
            QMessageBox.information(self, "Başarılı", message)
            self.stacked_widget.setCurrentWidget(self.tab_face)
        else:
            QMessageBox.warning(self, "Hata", message)

    def face_register(self):
        # Burada yüz kaydı işlemleri yapılabilir, örneğin veritabanına kaydetme işlemi

        QMessageBox.information(self, "Bilgi", "Yüzünüz başarıyla kaydedildi")
        self.stacked_widget.setCurrentWidget(self.tab_2fa)

    def face_verify(self):
        QMessageBox.information(self, "Bilgi", "Yüz doğrulama işlemi başlatıldı")

    def show_register_tab(self):
        self.stacked_widget.setCurrentWidget(self.register_widget)

    def show_login_tab(self):
        self.stacked_widget.setCurrentWidget(self.login_widget)

    def center_widgets(self, layout):
        layout.setAlignment(Qt.AlignCenter)
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)

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
                            padding: 8px;
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
                        QHBoxLayout, QVBoxLayout {
                            margin: 20px;
                        }
                    """)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
