import cv2 as cv
import numpy as np
import yaml
import io

'''
RMS: 3.3922481069548565
camera matrix:
 [[312.12837404700826, 0.0, 305.7373776912714]
 [ 0.0, 312.1160716398593, 175.39947207737023]
 [  0.           0.           1.        ]]
distortion coefficients:  [-0.05923006233886738  0.13273783139898743 -0.3144426393271996 -0.01334142  0.34210523]
([312.12837404700826, 0.0, 305.7373776912714]
[0.0, 312.1160716398593, 175.39947207737023]
[0.0, 0.0, 1.0])
([-0.05923006233886738]
[0.13273783139898743]
[-0.3144426393271996]
[0.23237501822988305])

'''
D = np.zeros((4))
K = np.zeros((3, 3))
def initPar():
    global D
    global K
    with open("/home/daniil/robototecnic/camcal/calibration/D.yaml", 'r') as stream:
        a = yaml.load(stream)
    
    D[0] = a['D0']
    D[1] = a['D1']
    D[2] = a['D2']
    D[3] = a['D3']
    K[0, 0] = a['K00']
    K[0, 1] = a['K01']
    K[0, 2] = a['K02']
    
    K[1, 0] = a['K10']
    K[1, 1] = a['K11']
    K[1, 2] = a['K12']
    K[2, 0] = a['K20']
    K[2, 1] = a['K21']
    K[2, 2] = a['K22']
initPar()
image = cv.imread("frame10.jpg")
h, w = image.shape[:2]
map1, map2 = cv.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, (w, h), cv.CV_16SC2)
img = cv.remap(image, map1, map2, interpolation=cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT)
cv.imshow("Calibrated", img)
while True:
    if(cv.waitKey(10) == 0x1b):
        cv.destroyAllWindows()
        break
#основные точки
top_left = [0,0] #520, 
top_right = [520, 0]
bottom_right = [520, 320]
bottom_left = [0,320]
pts = np.array([bottom_left,bottom_right,top_right,top_left])

#-----------
bottom_left_dst = [50, 276]         
bottom_right_dst = [618, 283]
top_right_dst = [458, 161]
top_left_dst = [181, 160]
dst_pts = np.array([bottom_left_dst, bottom_right_dst, top_right_dst, top_left_dst])
#вспомогательная отрисовка
preview=np.copy(img)
cv.polylines(preview,np.int32([dst_pts]),True,(0,0,255), 2)
#cv.polylines(preview,np.int32([pts]),True,(255,0,255), 1)

pts = np.float32(pts.tolist())
dst_pts = np.float32(dst_pts.tolist())
h, mask = cv.findHomography(dst_pts, pts)
#print(img.shape)

#image_size = img.shape[:2]
image_size = (560, 370)
warped = cv.warpPerspective(img, h, dsize = image_size, flags = cv.INTER_LINEAR)

gray = cv.cvtColor(warped, cv.COLOR_BGR2GRAY)
gray = cv.GaussianBlur(gray, (3, 3), 0)
(thresh, im_bw) = cv.threshold(gray, 110, 255, cv.THRESH_BINARY)
im_bw = cv.GaussianBlur(im_bw, (3, 3), 0)
cv.imshow("input image", image)
cv.imshow("Calibrated", img)
cv.imshow("preview", preview)
cv.imshow("warped", warped)
cv.imshow("edged", im_bw)
while True:
    if(cv.waitKey(10) == 0x1b):
        cv.destroyAllWindows()
        break
data = {'D0': D[0],
        'D1': D[1],
        'D2': D[2],
        'D3': D[3],
        'K00': K[0,0],
        'K01': K[0,1],
        'K02': K[0,2],
        'K10': K[1,0],
        'K11': K[1,1],
        'K12': K[1,2],
        'K20': K[2,0],
        'K21': K[2,1],
        'K22': K[2,2],
        'tl': top_left,
        #'tl':(0,0),
        'tr':top_right,
        'br':bottom_right,
        'bl':bottom_left,
        'bld':bottom_left_dst,
        'brd':bottom_right_dst,
        'trd':top_right_dst,
        'tld':top_left_dst
        }
with io.open('data_for_cam.yaml', 'w', encoding='utf8') as outfile:
    yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
    print("Written!")
