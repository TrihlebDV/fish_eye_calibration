import cv2
import numpy as np
 
image = cv2.imread('image.png',0)
size = np.size(image)
skel = np.zeros(image.shape,np.uint8)
 
ret,img = cv2.threshold(image,127,255,0)
cv2.imshow("treh", img)
cv2.imshow("orig", image)
while True:
    if cv2.waitKey(10) == 0x1b:
        cv2.destroyAllWindows()
        break
element = cv2.getStructuringElement(cv2.MORPH_CROSS,(3,3))
done = False
 
while( not done):
    eroded = cv2.erode(img,element)
    temp = cv2.dilate(eroded,element)
    temp = cv2.subtract(img,temp)
    skel = cv2.bitwise_or(skel,temp)
    img = eroded.copy()
 
    zeros = size - cv2.countNonZero(img)
    if zeros==size:
        done = True
''' 
cv2.imshow("skel",skel)
cv2.imshow("orig", image)
while True:
    if cv2.waitKey(10) == 0x1b:
        cv2.destroyAllWindows()
        break
try:
    cv2.imwrite("Sceletezeted.png", skel)
    print("Done")
except:
    print("Have a problem with CVwriting")
'''
