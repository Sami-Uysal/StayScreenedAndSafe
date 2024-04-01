from deepface import DeepFace


def face_detection(img1_path, img2_path):
    try:
        response = DeepFace.verify(img1_path, img2_path)
        sonuc = response["verified"]
        if sonuc:
            print("yüz tanıma başarılı")
        else:
            print("Yüz tanıma başarısız oldu, lütfen tekrar deneyin")
    except Exception as e:
        print("Hata:", e)
        print("Yüz tanıma işlemi gerçekleştirilemedi")

