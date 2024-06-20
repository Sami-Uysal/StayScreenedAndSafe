import cv2
from deepface import DeepFace
from faceVerified import foto_cektir


if __name__ == "__main__":
    adi = "" #adi değişkenine yazan yere qtui dan yüz doğrulama ya bastığımızda o anki saat ve tarihi ad şeklinde yapacaksın.
    dizin = "datasets/coco128/images/test/"
    kullaniciadi=""

    foto_cektir(adi, dizin)
#-------------------------------------------------------------------------------------------------------------------------------------



############################# Face Verification #############################################
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

img1_path = dizin + f"{kullaniciadi}" + ".jpg" #img1 uygulama içerisinde kullanıcın çektiği fotoğrafın pathini alıp buraya atayacağız.
img2_path = dizin + f"{adi}" + ".jpg" #img2 farklı açıdan bir fotoğraf daha alınacak.
face_detection(img1_path, img2_path)
###################################################################################################





