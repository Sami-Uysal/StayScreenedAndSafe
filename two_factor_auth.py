import os
import pyotp
import qrcode
from PyQt5.QtGui import QPixmap

users = {}  # Kullanıcı adı ve key'i saklamak için sözlük

def generate_qr_code(username, key):
    uri = pyotp.totp.TOTP(key).provisioning_uri(
        name=username,
        issuer_name='StayScreenedAndSafe')

    # QR kodunu kaydet
    os.makedirs("QR", exist_ok=True)
    qrcode.make(uri).save(os.path.join("QR", f"qr_{username}.png"))

def display_qr(username, qr_label):
    key = users.get(username)  # Varolan kullanıcı için key'i al
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
        users[username] = key
        generate_qr_code(username, key)
        display_qr(username, qr_label)
        return f"Kullanıcı '{username}' için QR kodu oluşturuldu."
    else:
        display_qr(username, qr_label)
        return f"Kullanıcı '{username}' için QR kodu gösterildi."
