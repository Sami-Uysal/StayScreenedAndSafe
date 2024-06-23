def login(self):
    username = self.login_username_entry.text()
    password = self.login_password_entry.text()

    if not username or not password:
        QMessageBox.warning(self, "Hata", "Kullanıcı adı ve parola boş bırakılamaz.")
        return

    self.logged_in_username = username

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