import cv2
import faceVerified








#-------------------------------------------web cam ile foto alma-----------------------------------------------------------------------------
def foto_cektir(adi, dizin):

    kamera = cv2.VideoCapture(0)


    ret, goruntu = kamera.read()

    if ret:

        cv2.imwrite(f"{dizin}/{adi}.jpg", goruntu)
        print(f"{adi}.jpg adlı dosya {dizin} dizinine kaydedildi.")
    else:
        print("Hata: Görüntü alınamadı.")

    # Kamerayı kapat
    kamera.release()


if __name__ == "__main__":
    adi = input("Dosya adını giriniz: ")
    dizin = "datasets/coco128/images/test/"

    foto_cektir(adi, dizin)
    #-------------------------------------------------------------------------------------------------------------------------------------



############################# Face Verification #############################################

img1_path = "datasets/coco128/images/test/3.jpg" #img1 uygulama içerisinde kullanıcın çektiği fotoğrafın pathini alıp buraya atayacağız.
img2_path = dizin + f"{adi}" + ".jpg" #img2 farklı açıdan bir fotoğraf daha alınacak.

faceVerified.face_detection(img1_path, img2_path)

###################################################################################################





