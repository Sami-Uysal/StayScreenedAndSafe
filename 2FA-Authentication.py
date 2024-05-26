import time
import pyotp
import qrcode
import os
import tkinter as tk
import tkinter.ttk as ttk

users = {}  # Kullanıcı adı ve key'i saklamak için sözlük

def generate_qr_code(username, key):
    uri = pyotp.totp.TOTP(key).provisioning_uri(
        name=username,
        issuer_name='StayScreenedAndSafe')

    # QR kodunu kaydet
    os.makedirs("QR", exist_ok=True)
    qrcode.make(uri).save(os.path.join("QR", f"qr_{username}.png"))

def display_qr(username):
    key = users.get(username)  # Varolan kullanıcı için key'i al
    if key:
        qr_image = tk.PhotoImage(file=os.path.join("QR", f"qr_{username}.png"))
        qr_label.configure(image=qr_image)
        qr_label.image = qr_image  # Tempi önlemek için referans görüntü
    else:
        print("Kullanıcı adı bulunamadı.")

def verify_code():
    username = username_entry.get()
    key = users.get(username)
    if not key:
        print("Kullanıcı adı bulunamadı.")
        return

    totp = pyotp.TOTP(key)
    code = code_entry.get()  # Kod girişi için entry'den oku
    if totp.verify(code):
        print("Giriş başarılı!")
    else:
        print("Kod hatalı. Tekrar deneyiniz.")

def generate_qr():
    username = username_entry.get()
    if username not in users:
        key = pyotp.random_base32()
        users[username] = key
        generate_qr_code(username, key)
        display_qr(username)
        print(f"Kullanıcı '{username}' için QR kodu oluşturuldu.")
    else:
        display_qr(username)
        print(f"Kullanıcı '{username}' için QR kodu gösterildi.")

    # Doğrulama arayüzü göster
    code_label.pack()
    code_entry.pack()
    verify_button.pack()

# Ana pencere oluşturma
root = tk.Tk()
root.title("2FA Uygulaması")

# Kullanıcı adı girişi
username_label = ttk.Label(root, text="Kullanıcı Adı:")
username_entry = ttk.Entry(root)

# Kod girişi (başlangıçta gizli)
code_label = ttk.Label(root, text="2FA Kodu:")
code_entry = ttk.Entry(root)

# QR kod görüntüleme
qr_label = ttk.Label(root)

# Butonlar
generate_button = ttk.Button(root, text="QR Kod Oluştur/Göster", command=generate_qr)
verify_button = ttk.Button(root, text="Kodu Doğrula", command=verify_code)

# Arayüz öğelerini pencere yerleştirme
username_label.pack()
username_entry.pack()
generate_button.pack()
qr_label.pack()

# Ana döngüyü başlatma
root.mainloop()
