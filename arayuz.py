import tkinter as tk
from tkinter import messagebox





def popup_mesaji_goster():
    messagebox.showinfo("Popup Mesajı", "Merhaba! Bu bir pop-up mesajıdır.")


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

# Pop-up mesajı gösteren düğmeyi oluştur
popup_dugme = tk.Button(root, text="Popup Mesajı Göster", command=popup_mesaji_goster)
popup_dugme.pack(pady=20)

# Uygulamayı başlat
root.mainloop()