import tkinter as tk
from tkinter import messagebox
import cv2
from PIL import Image, ImageTk

def kamera_goruntusu_goster():
    messagebox.showinfo("Yüz tanıma kayıt oluşturma",
                        "Lütfen sisteme yüzünüzü tanıtınız! dikkat yüzünüzün görünür çıktığından emin olunuz.")
    kamera = cv2.VideoCapture(0)
    while True:
        ret, frame = kamera.read()  # Kameradan bir kare
        if not ret:
            break
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (pencere_genislik, pencere_yukseklik))
        img = Image.fromarray(frame)
        img_tk = ImageTk.PhotoImage(image=img)  # tkinter için uygun format
        panel.img_tk = img_tk
        panel.config(image=img_tk)
        root.update()
    kamera.release()

def yuz_tanitma_baslat():
    kamera_goruntusu_goster()

root = tk.Tk()
root.title("StayScreenedAndSafe")

# Pencerenin boyutu
pencere_genislik = 600
pencere_yukseklik = 400
ekran_genislik = root.winfo_screenwidth()
ekran_yukseklik = root.winfo_screenheight()
x_pozisyon = (ekran_genislik - pencere_genislik) // 2
y_pozisyon = (ekran_yukseklik - pencere_yukseklik) // 2
root.geometry(f"{pencere_genislik}x{pencere_yukseklik}+{x_pozisyon}+{y_pozisyon}")


panel = tk.Label(root)
panel.pack(padx=10, pady=10)


popup_dugme = tk.Button(root, text="Yüz tanıtma başlat", command=yuz_tanitma_baslat)
popup_dugme.pack(pady=20, side="bottom")


root.mainloop()
