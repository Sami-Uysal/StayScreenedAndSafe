
import faceVerified



############################# Face Verification #############################################

img1_path = "datasets/coco128/images/test/2.jpg" #img1 uygulama içerisinde kullanıcın çektiği fotoğrafın pathini alıp buraya atayacağız.
img2_path = "datasets/coco128/images/test/3.jpg" #img2 farklı açıdan bir fotoğraf daha alınacak.

faceVerified.face_detection(img1_path, img2_path)

###################################################################################################



