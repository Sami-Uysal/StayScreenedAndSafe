<<<<<<< b9c9745ae53b05b0a673c74b29471aaa6af8439a
<<<<<<< b9c9745ae53b05b0a673c74b29471aaa6af8439a
=======
<<<<<<< HEAD
=======
>>>>>>> Fix errors
import cv2
import faceVerified







#-------------------------------------------web cam ile foto alma-----------------------------------------------------------------------------
def foto_cektir(adi, dizin):
    # Webcam'i aç
    kamera = cv2.VideoCapture(0)
>>>>>>> Revert "Update Yolov8 to DeepFace"

import faceVerified



############################# Face Verification #############################################

img1_path = "datasets/coco128/images/test/2.jpg" #img1 uygulama içerisinde kullanıcın çektiği fotoğrafın pathini alıp buraya atayacağız.
img2_path = "datasets/coco128/images/test/3.jpg" #img2 farklı açıdan bir fotoğraf daha alınacak.

faceVerified.face_detection(img1_path, img2_path)

###################################################################################################



<<<<<<< b9c9745ae53b05b0a673c74b29471aaa6af8439a
=======


<<<<<<< b9c9745ae53b05b0a673c74b29471aaa6af8439a
=======
>>>>>>> parent of b9c9745 (Update Yolov8 to DeepFace)
>>>>>>> Revert "Update Yolov8 to DeepFace"
=======
>>>>>>> Fix errors
