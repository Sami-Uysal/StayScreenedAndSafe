import time
import pyotp
import qrcode
import os

def generate_qr_code(username, key):
  uri = pyotp.totp.TOTP(key).provisioning_uri(
      name=username,
      issuer_name='StayScreenedAndSafe')

  print(uri)
  qrcode.make(uri).save(os.path.join("QR", f"qr_{username}.png"))

def verify_code(username, key):
  totp = pyotp.TOTP(key)
  code = input(f"{username} için kodu giriniz: ")
  return totp.verify(code)

users = {}

while True:
  username = input("Kullanıcı adınızı giriniz: ")

  if username in users:
    print(f"Kullanıcı '{username}' zaten kayıtlı.")
    continue

  key = pyotp.random_base32()

  users[username] = key

  generate_qr_code(username, key)

  while True:
    if verify_code(username, key):
      print("Giriş başarılı!")
      break
    else:
      print("Kod hatalı. Tekrar deneyiniz.")

