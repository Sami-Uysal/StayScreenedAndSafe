import cv2
import base64
from deepface import DeepFace
import os


def yuz_kayit(username):
    kamera = cv2.VideoCapture(0)
    ret, goruntu = kamera.read()
    kamera.release()

    if ret:
        temp_dir = "Temp"
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, f"{username}_temp.jpg")
        cv2.imwrite(temp_path, goruntu)

        return temp_path
    else:
        print("Hata: Görüntü alınamadı.")
        return None

def yuz_dogrula(registered_face_data, error=0):
    if error == 3:
        return False
    else:
        try:
            kamera = cv2.VideoCapture(0)
            ret, goruntu = kamera.read()
            kamera.release()

            if ret:
                temp_dir = "Temp"
                os.makedirs(temp_dir, exist_ok=True)

                temp_path = os.path.join(temp_dir, "temp.jpg")
                cv2.imwrite(temp_path, goruntu)

                registered_temp_path = os.path.join(temp_dir, "registered_temp.jpg")

                image_data = base64.b64decode(registered_face_data)
                with open(registered_temp_path, "wb") as f:
                    f.write(image_data)

                if not os.path.exists(temp_path):
                    raise FileNotFoundError(f"Geçici görüntü şu adreste bulunamadı {temp_path}")

                if not os.path.exists(registered_temp_path):
                    raise FileNotFoundError(f"Kayıtlı geçici görüntü şu adreste bulunamadı {registered_temp_path}")

                result = DeepFace.verify(img1_path=registered_temp_path, img2_path=temp_path)

                os.remove(temp_path)
                os.remove(registered_temp_path)

                if result["verified"]:
                    print("Yüz doğrulama başarılı.")
                else:
                    return yuz_dogrula(registered_face_data, error + 1)

                return result["verified"]
            else:
                print("Hata: Görüntü alınamadı.")
                return yuz_dogrula(registered_face_data, error + 1)
        except Exception as e:
            print(f"Hata: {str(e)}")
            return yuz_dogrula(registered_face_data, error + 1)



