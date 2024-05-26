import tkinter as tk
from tkinter import messagebox

def popup_mesaji_goster(message):
    messagebox.showinfo("Bilgi", message)

def yuz_kayit():
    popup_mesaji_goster("Yüzünüz başarıyla kaydedildi")

def yuz_dogrulama():
    popup_mesaji_goster("Yüz doğrulama işlemi başlatıldı")

root = tk.Tk()
root.title("StayScreenedAndSafe")

pencere_genislik = 600
pencere_yukseklik = 400
ekran_genislik = root.winfo_screenwidth()
ekran_yukseklik = root.winfo_screenheight()
x_pozisyon = (ekran_genislik - pencere_genislik) // 2
y_pozisyon = (ekran_yukseklik - pencere_yukseklik) // 2
root.geometry(f"{pencere_genislik}x{pencere_yukseklik}+{x_pozisyon}+{y_pozisyon}")

yuz_kayit_dugme = tk.Button(root, text="Yüz Kayıt", command=yuz_kayit)
yuz_kayit_dugme.pack(pady=20, padx=10, side=tk.LEFT)

yuz_dogrulama_dugme = tk.Button(root, text="Yüz Doğrulama", command=yuz_dogrulama)
yuz_dogrulama_dugme.pack(pady=20, padx=10, side=tk.LEFT)

root.mainloop()
