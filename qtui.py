import base64
import sys
import pyotp
import os
from mysql.connector import Error
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, \
    QLineEdit, QPushButton, QStackedWidget
from PyQt5.QtCore import Qt
from two_factor_auth import generate_qr_code, display_qr, verify_code, save_secret_key
import mysqlconnect
import cv2
from faceVerified import yuz_kayit, yuz_dogrula
import numpy as np
import re

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
        self.setup_configure_tab()
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

        self.show_face_image_button = QPushButton("Kayıtlı Yüzü Göster")
        self.show_face_image_button.clicked.connect(self.show_face_image)

        self.show_face_label = QLabel()

        self.logout_button = QPushButton("Çıkış Yap")
        self.logout_button.clicked.connect(self.logout)

        layout.addWidget(self.face_register_button)
        layout.addWidget(self.face_verify_button)
        layout.addWidget(self.show_face_image_button)
        layout.addWidget(self.show_face_label)
        layout.addWidget(self.logout_button)

        # Uygulama yapılandır butonunu ekle
        self.configure_button = QPushButton("Uygulama Yapılandır")
        self.configure_button.clicked.connect(self.show_configure_tab)
        layout.addWidget(self.configure_button)

        self.center_widgets(layout)
        self.tab_face.setLayout(layout)
        self.stacked_widget.addWidget(self.tab_face)

    def setup_configure_tab(self):
        self.tab_configure = QWidget()
        layout = QVBoxLayout()

        label = QLabel("Uygulama Yapılandırma Sayfası")
        label.setAlignment(Qt.AlignCenter)

        # Dakika değerini girebileceğimiz bir QLineEdit oluşturalım
        self.interval_label = QLabel("Dakika da bir yüz doğrulaması yapsın:")
        self.interval_entry = QLineEdit()
        self.interval_entry.setPlaceholderText("Dakika sayısını giriniz")

        # Ayarları Kaydet butonu
        self.save_button = QPushButton("Ayarları Kaydet")
        self.save_button.clicked.connect(self.save_configuration)

        layout.addWidget(label)
        layout.addWidget(self.interval_label)
        layout.addWidget(self.interval_entry)
        layout.addWidget(self.save_button)

        self.center_widgets(layout)
        self.tab_configure.setLayout(layout)
        self.stacked_widget.addWidget(self.tab_configure)

    def save_configuration(self):
        interval_minutes = self.interval_entry.text()

        try:
            # Burada interval_minutes'i istediğiniz şekilde kullanabilirsiniz
            # Örneğin, veritabanına kaydedebilirsiniz veya uygulama içinde kullanabilirsiniz
            QMessageBox.information(self, "Bilgi",
                                    f"Ayarlar kaydedildi: Yüz doğrulaması her {interval_minutes} dakikada bir yapılacak.")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Ayarları kaydederken bir hata oluştu: {e}")

    def sample_config_action(self):
        QMessageBox.information(self, "Yapılandırma", "Örnek yapılandırma işlemi gerçekleştirildi!")

    def logout(self):
        self.logged_in_username = ""  # Kullanıcıyı oturumdan çıkar
        self.show_login_tab()  # Giriş ekranına dön

    def register(self):
        username = self.register_username_entry.text()
        email = self.register_email_entry.text()
        password = self.register_password_entry.text()

        # Türkçe karakterleri kontrol eden regex
        turkish_characters = re.compile(r'[çÇğĞıİöÖşŞüÜ]')

        if not username or not email or not password:
            QMessageBox.warning(self, "Hata", "Lütfen tüm alanları doldurun.")
            return

        if turkish_characters.search(username):
            QMessageBox.warning(self, "Hata", "Lütfen kullanıcı adında Türkçe karakter kullanmayın.")
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)",
                           (username, password, email))
            self.connection.commit()
            QMessageBox.information(self, "Kayıt Başarılı", f"Kullanıcı {username} başarıyla kaydedildi!")

            # Kullanıcı kaydedildikten sonra 2FA işlemleri için gerekli kontrolleri yapın
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user:
                cursor.execute("SELECT * FROM two_factor_data WHERE user_id = %s", (user[0],))
                two_fa_data = cursor.fetchone()

                if not two_fa_data:
                    key = pyotp.random_base32()
                    save_secret_key(username, key)
                    generate_qr_code(username)
                    display_qr(username, self.qr_label_2fa)
                    self.stacked_widget.setCurrentWidget(self.tab_2fa)
                else:
                    QMessageBox.warning(self, "Bilinmeyen bir hata", "2FA secret key value not found!")

            cursor.close()

        except Error as e:
            QMessageBox.warning(self, "Veritabanı Hatası", f"Hata: {e}")

    def login(self):
        username = self.login_username_entry.text()
        password = self.login_password_entry.text()

        if not username or not password:
            QMessageBox.warning(self, "Hata", "Lütfen kullanıcı adı ve parola girin.")
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cursor.fetchone()
            if user:
                self.logged_in_username = username  # Kullanıcı adı kaydedildi
                QMessageBox.information(self, "Giriş Başarılı", f"Hoş geldiniz, {username}!")
                self.stacked_widget.setCurrentWidget(self.tab_face)  # Yüz doğrulama sekmesine geç
            else:
                QMessageBox.warning(self, "Hata", "Geçersiz kullanıcı adı veya parola.")
            cursor.close()
        except Error as e:
            QMessageBox.warning(self, "Veritabanı Hatası", f"Hata: {e}")

    def generate_qr(self):
        username = self.register_username_entry.text()  # Kullanıcı adını register ekranından çek
        display_qr(username, self.qr_label_2fa)

    def verify_code(self):
        username = self.register_username_entry.text()
        code = self.code_entry.text()
        if verify_code(username, code):
            QMessageBox.information(self, "Doğrulama Başarılı", "2FA kodu doğrulandı!")
            self.stacked_widget.setCurrentWidget(self.tab_face)  # Yüz kaydı sekmesine geç
        else:
            QMessageBox.warning(self, "Doğrulama Hatası", "Geçersiz 2FA kodu.")

    def face_register(self):
        username = self.logged_in_username

        # Yüz fotoğrafı çek
        temp_image_path = yuz_kayit(username)

        if temp_image_path is not None:
            try:
                cursor = self.connection.cursor()

                # Kullanıcının ID'sini al
                cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
                user_id = cursor.fetchone()[0]

                # Yüz verisini veritabanına kaydet
                with open(temp_image_path, 'rb') as image_file:
                    image_data = image_file.read()
                    image_base64 = base64.b64encode(image_data).decode('utf-8')

                temp_dir = "Temp"
                os.makedirs(temp_dir, exist_ok=True)
                image_path = os.path.join(temp_dir, f"{username}_registered.jpg".encode('utf-8').decode('utf-8'))

                # Kullanıcının yüz verisi olup olmadığını kontrol et
                cursor.execute("SELECT id FROM face_data WHERE user_id = %s", (user_id,))
                existing_face_data = cursor.fetchone()

                if existing_face_data:
                    # Var olan yüz verisini güncelle
                    cursor.execute("""
                        UPDATE face_data
                        SET image_path = %s, image = %s
                        WHERE user_id = %s
                    """, (image_path, image_base64, user_id))
                else:
                    # Yeni yüz verisi ekle
                    cursor.execute("""
                        INSERT INTO face_data (user_id, image_path, image)
                        VALUES (%s, %s, %s)
                    """, (user_id, image_path, image_base64))

                self.connection.commit()
                cursor.close()

                # Görüntüyü geçici dosya sistemine kaydet
                os.rename(temp_image_path, image_path)

                QMessageBox.information(self, "Bilgi", "Yüzünüz başarıyla kaydedildi")
                self.stacked_widget.setCurrentWidget(self.tab_face)

                # İşlemler tamamlandıktan sonra geçici dosyaları sil
                os.remove(image_path)
            except Error as e:
                QMessageBox.warning(self, "Veritabanı Hatası", f"Hata: {e}")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Bilinmeyen bir hata oluştu: {e}")
            finally:
                if cursor:
                    cursor.close()
                if os.path.exists(temp_image_path):
                    os.remove(temp_image_path)
        else:
            QMessageBox.warning(self, "Hata", "Görüntü alınamadı.")

    def show_face_image(self):
        username = self.logged_in_username

        try:
            cursor = self.connection.cursor()

            # Kullanıcının ID'sini al
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            user_id = cursor.fetchone()

            if user_id is None:
                QMessageBox.warning(self, "Hata", "Bu kullanıcı adı için kayıtlı yüz yok. Lütfen yüz kaydı yapın.")
                return

            user_id = user_id[0]

            # Yüz verisini veritabanından çek
            cursor.execute("SELECT image FROM face_data WHERE user_id = %s", (user_id,))
            image_data = cursor.fetchone()
            cursor.close()

            if image_data is None:
                QMessageBox.warning(self, "Hata", "Bu kullanıcı adı için kayıtlı yüz yok. Lütfen yüz kaydı yapın.")
                return

            image_data = image_data[0]

            # Base64 verisini çöz
            image_data = base64.b64decode(image_data)
            nparr = np.frombuffer(image_data, np.uint8)
            img_np = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

            # OpenCV görüntüsünü QImage'e dönüştür
            height, width, channel = img_np.shape
            bytes_per_line = 3 * width
            q_img = QImage(img_np.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()

            # QImage'i QLabel'de göster
            self.show_face_label.setPixmap(QPixmap.fromImage(q_img))
            self.stacked_widget.setCurrentWidget(self.tab_face)
        except Error as e:
            QMessageBox.warning(self, "Veritabanı Hatası", f"Hata: {e}")

    def face_verify(self):
        username = self.login_username_entry.text()
        if not username:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir kullanıcı adı girin")
            return

        try:
            cursor = self.connection.cursor()

            # Kullanıcının ID'sini al
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if not user:
                QMessageBox.warning(self, "Hata", "Bu kullanıcı adı için kayıtlı kullanıcı yok")
                return

            user_id = user[0]

            # Yüz verisinin olup olmadığını kontrol et
            cursor.execute("SELECT image FROM face_data WHERE user_id = %s", (user_id,))
            face_data = cursor.fetchone()
            cursor.close()

            if not face_data:
                QMessageBox.warning(self, "Hata", "Bu kullanıcı adı için kayıtlı yüz yok. Lütfen yüz kaydı yapın.")
                return

            registered_face_data = face_data[0]

            # Yüz doğrulama işlemi
            if yuz_dogrula(registered_face_data):
                QMessageBox.information(self, "Başarı", "Yüz başarıyla doğrulandı")
                self.show_configure_button()
                self.stacked_widget.setCurrentWidget(self.tab_face)  # Ana sayfaya yönlendir
            else:
                QMessageBox.warning(self, "Hata", "Yüz doğrulama başarısız oldu")

        except Exception as e:
            QMessageBox.warning(self, "Veritabanı Hatası", f"Hata: {e}")

    def show_configure_button(self):
        self.configure_button = QPushButton("Uygulamayı Yapılandır")
        self.configure_button.clicked.connect(self.show_configure_tab)
        self.tab_face.layout().addWidget(self.configure_button)

    def show_configure_tab(self):
        self.stacked_widget.setCurrentWidget(self.tab_configure)

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