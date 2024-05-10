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
    qrcode.make(uri).save(os.path.join("QR", f"qr_{username}.png"))

def display_qr(username):
    key = users.get(username)  # Varolan kullanıcı için key'i al
    if key:
        qr_image = tk.PhotoImage(file=os.path.join("QR", f"qr_{username}.png"))
        qr_label.configure(image=qr_image)
        qr_label.image = qr_image  # Tempi önlemek için referans görüntü
    else:
        print("Kullanıcı adı bulunamadı.")

def verify_code(username, key):
    totp = pyotp.TOTP(key)
    code = code_entry.get()  # Kod girişi için entry'den oku
    return totp.verify(code)

def generate_and_verify():
    username = username_entry.get()
    if username not in users:
        key = pyotp.random_base32()
        users[username] = key
        generate_qr_code(username, key)
        display_qr(username)
        print(f"Kullanıcı '{username}' için QR kodu oluşturuldu.")
    else:
        display_qr(username)

    if verify_code(username, users[username]):
        print("Giriş başarılı!")
    else:
        print("Kod hatalı. Tekrar deneyiniz.")

# Ana pencere oluşturma
root = tk.Tk()
root.title("2FA Uygulaması")

# Kullanıcı adı girişi
username_label = ttk.Label(root, text="Kullanıcı Adı:")
username_entry = ttk.Entry(root)

# Kod girişi
code_label = ttk.Label(root, text="2FA Kodu:")
code_entry = ttk.Entry(root)

# QR kod görüntüleme
qr_label = ttk.Label(root)

# Butonlar
generate_button = ttk.Button(root, text="QR Kod Oluştur/Göster", command=generate_and_verify)

# Arayüz öğelerini pencere yerleştirme
username_label.pack()
username_entry.pack()
code_label.pack()
code_entry.pack()
qr_label.pack()
generate_button.pack()

# Ana döngüyü başlatma
root.mainloop()
