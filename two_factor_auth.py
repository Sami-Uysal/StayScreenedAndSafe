import os
import pyotp
import qrcode
from mysql.connector import Error
import mysqlconnect
from PyQt5.QtGui import QPixmap

# Kullanıcıların ve onların gizli anahtarlarının veritabanından alınmasını sağlayan fonksiyon
def fetch_user_secret_key(username):
    connection = mysqlconnect.create_connection()
    if connection is None:
        return None
    try:
        cursor = connection.cursor()
        cursor.execute(
            "SELECT t.secret_key FROM users u JOIN two_factor_data t ON u.id = t.user_id WHERE u.username = %s",
            (username,))
        result = cursor.fetchone()
        if result:
            secret_key = result[0]
            return secret_key
        else:
            return None
    except Error as e:
        print(f"Kullanıcı gizli anahtarı alınırken hata oluştu: {e}")
        return None
    finally:
        if connection.is_connected():
            connection.close()

# Kullanıcı için gizli anahtar oluşturan ve veritabanına kaydeden fonksiyon
def save_secret_key(username, key):
    connection = mysqlconnect.create_connection()
    if connection is None:
        return None
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user_id = cursor.fetchone()[0]
        cursor.execute("INSERT INTO two_factor_data (user_id, secret_key) VALUES (%s, %s)", (user_id, key))
        connection.commit()
        return True
    except Error as e:
        print(f"Gizli anahtar kaydedilirken hata oluştu: {e}")
        return False
    finally:
        if connection.is_connected():
            connection.close()

# Bir kullanıcı için QR kodu oluşturan fonksiyon
def generate_qr_code(username):
    key = fetch_user_secret_key(username)
    if key:
        # Gizli anahtar kullanılarak TOTP (Zaman Temelli Tek Kullanımlık Şifre) için URI oluşturma
        uri = pyotp.totp.TOTP(key).provisioning_uri(
            name=username,
            issuer_name='StayScreenedAndSafe')

        # QR kodu resmini dosyaya kaydetme
        os.makedirs("QR", exist_ok=True)
        qrcode.make(uri).save(os.path.join("QR", f"qr_{username}.png"))
        return True, f"{username} için QR kodu başarıyla oluşturuldu."
    else:
        return False, f"QR kodu oluşturma başarısız. {username} kullanıcısı bulunamadı."

# Bir kullanıcının QR kodunu QLabel içinde gösteren fonksiyon
def display_qr(username, qr_label):
    key = fetch_user_secret_key(username)
    if key:
        qr_image_path = os.path.join("QR", f"qr_{username}.png")
        pixmap = QPixmap(qr_image_path)
        qr_label.setPixmap(pixmap)
    else:
        qr_label.clear()
        qr_label.setText("Kullanıcı adı bulunamadı.")

# Kullanıcının girdiği kodu, kayıtlı gizli anahtarıyla karşılaştırıp doğrulayan fonksiyon
def verify_code(username, code):
    key = fetch_user_secret_key(username)
    if not key:
        return False, "Kullanıcı adı bulunamadı."

    totp = pyotp.TOTP(key)
    if totp.verify(code):
        return True, "Giriş başarılı!"
    else:
        return False, "Kod hatalı. Tekrar deneyiniz."

# Kullanıcı adı verilen bir kullanıcının bilgilerini döndüren fonksiyon
def get_user_info(username):
    connection = mysqlconnect.create_connection()
    if connection is None:
        return None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        return user
    except Error as e:
        print(f"Kullanıcı bilgilerini alırken hata oluştu: {e}")
        return None
    finally:
        if connection.is_connected():
            connection.close()
