import base64
import sys
import pyotp
import os
import sys
import time
from threading import Thread
from mysql.connector import Error
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, \
    QLineEdit, QPushButton, QStackedWidget, QDialog, QSpinBox, QSystemTrayIcon, QAction, QMenu
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from two_factor_auth import generate_qr_code, display_qr, verify_code, save_secret_key
import mysqlconnect
import cv2
from faceVerified import yuz_kayit, yuz_dogrula
import numpy as np
import re
import ctypes

class ConfigDialog(QDialog):
    def __init__(self, parent=None):
        super(ConfigDialog, self).__init__(parent)
        self.setWindowTitle('Aralığı Yapılandırma')
        self.interval_input = QSpinBox(self)
        self.interval_input.setSuffix(' dakika')
        self.interval_input.setRange(1, 120)
        self.interval_input.setValue(5)
        self.save_button = QPushButton('Kaydet', self)
        self.save_button.clicked.connect(self.save_config)
        layout = QVBoxLayout()
        layout.addWidget(self.interval_input)
        layout.addWidget(self.save_button)
        self.setLayout(layout)
        self.interval = 5

    def save_config(self):
        interval = self.interval_input.value()
        self.parent().config_dialog.interval = interval
        username = self.parent().logged_in_username
        registered_face_data = self.parent().get_registered_face_data(username)
        configure_and_start_recognition(interval, registered_face_data, self)  # Burada registered_face_data eklenmeli
        QMessageBox.information(self, "Bilgi", f"Ayarlar kaydedildi: Yüz doğrulaması her {interval} dakikada bir yapılacak.")
        self.accept()



class MainWindow(QMainWindow):
    face_recognition_success = pyqtSignal()
    face_recognition_failure = pyqtSignal()
    def __init__(self):
        super(MainWindow, self).__init__()

        self.setup_system_tray()
        self.setup_main_window()
        self.setup_mysql_connection()
        self.setup_layout()
        self.setup_tabs()
        self.apply_styles()

        self.face_recognition_success.connect(self.on_face_recognition_success)
        self.face_recognition_failure.connect(self.on_face_recognition_failure)




    def on_face_recognition_success(self):
        QMessageBox.information(self, "Başarı", "Yüz başarıyla doğrulandı")

    def on_face_recognition_failure(self):

        self.show()
        self.stacked_widget.setCurrentWidget(self.tab_2fa)
        self.start_timer()
        QMessageBox.warning(self, "Hata", "Yüz doğrulama başarısız oldu.Lütfen 2FA kodunu girin.")

    def setup_system_tray(self):
        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon('sssLogo.png'))

        show_action = QAction('Göster', self)
        #quit_action = QAction('Çık', self)
        hide_action = QAction('Gizle', self)

        show_action.triggered.connect(self.show)
       # quit_action.triggered.connect(self.prevent_close)
        hide_action.triggered.connect(self.hide)

        tray_menu = QMenu()
        tray_menu.addAction(show_action)
        tray_menu.addAction(hide_action)
       # tray_menu.addAction(quit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

    def setup_main_window(self):
        self.setWindowTitle("StayScreenedAndSafe")
        self.setGeometry(100, 100, 800, 600)

    def setup_mysql_connection(self):
        self.connection = mysqlconnect.create_connection()
        if self.connection is None:
            QMessageBox.critical(self, "Bağlantı Hatası", "MySQL veritabanına bağlanılamadı.")
            sys.exit(1)

    def setup_layout(self):
        main_layout = QVBoxLayout()

        # Logo ekle
        self.logo_label = QLabel()
        self.logo_label.setPixmap(QPixmap("sssLogo - Kopya (2).png").scaled(1920, 300, Qt.KeepAspectRatio))
        self.logo_label.setAlignment(Qt.AlignCenter)

        self.stacked_widget = QStackedWidget()

        main_layout.addWidget(self.logo_label)
        main_layout.addWidget(self.stacked_widget)

        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

    def prevent_close(self):
        # Kullanıcı çıkış yapmak istediğinde uyarı ver ve çıkışı engelle
        QMessageBox.warning(self, "Uyarı",
                            "Çıkış yapmak için sağ tık menüsünden 'Çıkış'ı seçemezsiniz. Uygulamayı kapatmak için 'Gizle' seçeneğini kullanabilirsiniz.")
    def setup_tabs(self):
        self.setup_login_tab()
        self.setup_register_tab()
        self.setup_2fa_tab()
        self.setup_face_tab()
        self.setup_configure_tab()
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

    def get_registered_face_data(self, username):
        try:
            cursor = self.connection.cursor()
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()
            if not user:
                return None
            user_id = user[0]
            cursor.execute("SELECT image FROM face_data WHERE user_id = %s", (user_id,))
            face_data = cursor.fetchone()
            cursor.close()
            if not face_data:
                return None
            return face_data[0]
        except Error as e:
            QMessageBox.warning(self, "Veritabanı Hatası", f"Hata: {e}")
            return None

    def setup_2fa_tab(self):
        self.tab_2fa = QWidget()
        layout = QVBoxLayout()

        # Timer labelı ve bilgilendirme metni
        self.timer_label = QLabel(
            "2FA kodunu giriniz, aksi takdirde oturum 30 saniye içinde kilitlenecek. Kalan süre: 30 saniye")
        self.timer_label.setAlignment(Qt.AlignCenter)  # Ortala
        layout.addWidget(self.timer_label)

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

        # Timer ayarlaması
        self.countdown_timer = QTimer(self)
        self.countdown_timer.timeout.connect(self.update_timer)
        self.time_remaining = 30  # Oturum kilitlenme süresi saniye cinsinden

    def start_timer(self):
        # Timer'ı başlat
        self.countdown_timer.start(1000)  # 1 saniye aralıklarla çalışacak

    def update_timer(self):
        if self.time_remaining > 0:
            self.timer_label.setText(f"2FA kodunu giriniz, aksi takdirde oturum 30 saniye içinde kilitlenecek. Kalan süre: {self.time_remaining} saniye")
            self.time_remaining -= 1
        else:
            self.timer_label.setText("Oturum kilitlendi!")
            self.countdown_timer.stop()
            self.lock_windows_session()  # Oturumu kitleme işlemi

    def on_2fa_tab_selected(self):
        # 2FA sekmesi seçildiğinde timer'ı başlat
        self.start_timer()

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

        self.configure_button = QPushButton("Uygulama Yapılandır")
        self.configure_button.clicked.connect(self.show_configure_tab)
        layout.addWidget(self.configure_button)

        self.center_widgets(layout)
        self.tab_face.setLayout(layout)
        self.stacked_widget.addWidget(self.tab_face)

    def setup_configure_tab(self):
        self.tab_configure = QWidget()

        # Label for the configuration page
        label = QLabel("Uygulama Yapılandırma Sayfası")
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("font-size: 18px; color: #1abc9c;")

        # Interval configuration
        self.interval_label = QLabel("Kaç dakika da bir yüz doğrulaması yapılmalı:")
        self.interval_label.setStyleSheet("font-size: 14px; color: #2c3e50;")

        self.interval_input = QSpinBox()
        self.interval_input.setSuffix(' dakika')
        self.interval_input.setRange(1, 120)
        self.interval_input.setValue(5)

        # Save configuration button
        self.save_config_button = QPushButton("Ayarları Kaydet")
        self.save_config_button.clicked.connect(self.save_config)
        self.save_config_button.setStyleSheet("background-color: #1abc9c; color: #ecf0f1;")

        # Return to main page button
        self.return_to_main_button = QPushButton("Ana Sayfaya Dön")
        self.return_to_main_button.clicked.connect(self.show_face_tab)
        self.return_to_main_button.setStyleSheet("background-color: #e74c3c; color: #ecf0f1;")

        # Layout for the tab_configure
        layout = QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.interval_label)
        layout.addWidget(self.interval_input)
        layout.addWidget(self.save_config_button)
        layout.addWidget(self.return_to_main_button)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        self.tab_configure.setLayout(layout)
        self.stacked_widget.addWidget(self.tab_configure)

    def show_face_tab(self):
        self.stacked_widget.setCurrentWidget(self.tab_face)

    def save_config(self):
        interval = self.interval_input.value()
        configure_and_start_recognition(interval, self.get_registered_face_data(self.logged_in_username), self)
        QMessageBox.information(self, "Bilgi", f"Ayarlar kaydedildi: Yüz doğrulaması her {interval} dakikada bir yapılacak.")


    def register(self):
        username = self.register_username_entry.text()
        email = self.register_email_entry.text()
        password = self.register_password_entry.text()
        print(username + " register username testi")
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
        print(username + " login username testi")
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
        print(username + " generate_qr username testi")

    def verify_code(self):
        username = self.register_username_entry.text() if self.register_username_entry.text() else self.login_username_entry.text()

        print(username+" verify_code username testi")
        code = self.code_entry.text()
        if verify_code(username, code):
            QMessageBox.information(self, "Doğrulama Başarılı", "2FA kodu doğrulandı!")
            self.stacked_widget.setCurrentWidget(self.tab_face)  # Yüz kaydı sekmesine geç
        else:
            self.lock_windows_session()
            QMessageBox.warning(self, "Doğrulama Hatası", "Geçersiz 2FA kodu.")


    def lock_windows_session(self):
        ctypes.windll.user32.LockWorkStation()
    def verify_code_login(self):
        username = self.login_username_entry.text()
        code = self.code_entry.text()
        print(username + " verify_code_login username testi")
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
            if yuz_dogrula(registered_face_data, error=0):
                self.face_recognition_success.emit()
                self.stacked_widget.setCurrentWidget(self.tab_face)
            else:
                self.face_recognition_failure.emit()

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
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QLabel {
                font-size: 14px;
                color: #ecf0f1;
            }
            QLineEdit {
                background-color: #34495e;
                color: #ecf0f1;
                padding: 5px;
                border: 1px solid #1abc9c;
            }
            QPushButton {
                background-color: #1abc9c;
                color: #ecf0f1;
                padding: 10px;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #16a085;
            }
            QMessageBox {
                background-color: #34495e;
                color: #ecf0f1;
                border: 2px solid #1abc9c;
            }
            QMessageBox QPushButton {
                background-color: #1abc9c;
                color: #ecf0f1;
                padding: 5px;
                border: none;
                border-radius: 3px;
            }
            QMessageBox QPushButton:hover {
                background-color: #16a085;
            }           
        """)

    def logout(self):
        self.stacked_widget.setCurrentWidget(self.login_widget)
    def closeEvent(self, event):
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "StayScreenedAndSafe",
            "Uygulama sistem tepsisine taşındı.",
            QIcon('sssLogo.png'),
            2000
        )


def start_face_recognition(interval, registered_face_data, window_instance):
    def recognize_faces_periodically():
        while True:
            if yuz_dogrula(registered_face_data, error=0):
                window_instance.face_recognition_success.emit()
            else:
                window_instance.face_recognition_failure.emit()

            time.sleep(interval * 60)

    recognition_thread = Thread(target=recognize_faces_periodically)
    recognition_thread.daemon = True
    recognition_thread.start()


def configure_and_start_recognition(user_interval, registered_face_data, window_instance):
    start_face_recognition(user_interval, registered_face_data, window_instance)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    icon_path = "sssLogo - Kopya.png"
    window = MainWindow()
    window.setWindowIcon(QIcon(icon_path))
    window.show()
    sys.exit(app.exec_())