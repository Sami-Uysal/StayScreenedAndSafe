import time
import pyotp
import qrcode

key = "StayScreenedAndSafe2FA"

uri = pyotp.totp.TOTP(key).provisioning_uri(
	name='SamiUysal',
	issuer_name='StayScreenedAndSafe')

print(uri)

qrcode.make(uri).save("qr.png")

totp = pyotp.TOTP(key)

while True:
    print(totp.verify(input(("Enter the Code : "))))
