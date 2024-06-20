import cv2




#-------------------------------------------web cam ile foto alma-----------------------------------------------------------------------------
def foto_cektir(adi):
    dizin = "datasets/coco128/images/test/"
    kamera = cv2.VideoCapture(0)


    ret, goruntu = kamera.read()

    if ret:

        cv2.imwrite(f"{dizin}/{adi}.jpg", goruntu)
        print(f"{adi}.jpg adlı dosya {dizin} dizinine kaydedildi.")
    else:
        print("Hata: Görüntü alınamadı.")

    # Kamerayı kapat
    kamera.release()


def yuz_kayit():
    kamera = cv2.VideoCapture(0)
    ret, goruntu = kamera.read()
    kamera.release()

    if ret:
        return goruntu
    else:
        print("Hata: Görüntü alınamadı.")
        return None