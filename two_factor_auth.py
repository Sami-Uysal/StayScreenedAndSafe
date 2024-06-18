import os
import pyotp
import qrcode
import mysqlconnect
from mysql.connector import Error
from PyQt5.QtGui import QPixmap

def fetch_users_from_db():
    connection = mysqlconnect.create_connection()
    if connection is None:
        return {}
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT u.username, t.secret_key FROM users u JOIN two_factor_data t ON u.id = t.user_id")
        result = cursor.fetchall()
        users = {row[0]: row[1] for row in result}
        cursor.close()
        connection.close()
        return users
    except Error as e:
        print(f"Error fetching users: {e}")
        return {}

def add_user_to_db(username, key):
    connection = mysqlconnect.create_connection()
    if connection is None:
        return False
    try:
        cursor = connection.cursor()
        cursor.execute("INSERT INTO users (username, password, mail) VALUES (%s, %s)", (username, "123456", username+"@gmail.com"))  # Varsayılan bir şifre kullanın
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO two_factor_data (user_id, secret_key) VALUES (%s, %s)", (user_id, key))
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Error as e:
        print(f"Error adding user: {e}")
        return False

users = fetch_users_from_db()

def generate_qr_code(username, key):
    uri = pyotp.totp.TOTP(key).provisioning_uri(
        name=username,
        issuer_name='StayScreenedAndSafe')

    # QR kodunu kaydet
    os.makedirs("QR", exist_ok=True)
    qrcode.make(uri).save(os.path.join("QR", f"qr_{username}.png"))

def display_qr(username, qr_label):
    key = users.get(username)
    if key:
        qr_image_path = os.path.join("QR", f"qr_{username}.png")
        pixmap = QPixmap(qr_image_path)
        qr_label.setPixmap(pixmap)
    else:
        qr_label.clear()
        qr_label.setText("Kullanıcı adı bulunamadı.")

def verify_code(username, code):
    key = users.get(username)
    if not key:
        return False, "Kullanıcı adı bulunamadı."

    totp = pyotp.TOTP(key)
    if totp.verify(code):
        return True, "Giriş başarılı!"
    else:
        return False, "Kod hatalı. Tekrar deneyiniz."

def generate_qr(username, qr_label):
    if username not in users:
        key = pyotp.random_base32()
        if add_user_to_db(username, key):
            users[username] = key
            generate_qr_code(username, key)
            display_qr(username, qr_label)
            return f"Kullanıcı '{username}' için QR kodu oluşturuldu."
        else:
            return "Kullanıcı eklenirken bir hata oluştu."
    else:
        display_qr(username, qr_label)
        return f"Kullanıcı '{username}' için QR kodu gösterildi."
