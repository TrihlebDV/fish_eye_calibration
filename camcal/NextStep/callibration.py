import sys  # sys нужен для передачи argv в QApplication
import os  # Отсюда нам понадобятся методы для отображения содержимого директорий

from PyQt5 import QtWidgets, QtGui
from PyQt5.QtCore import Qt, pyqtSignal, QObject
import numpy as np
from time import sleep
import threading
import com_des  # Это наш конвертированный файл дизайна
import cv2 as cv
import yaml
import io
import math


class ExampleApp(QtWidgets.QMainWindow, com_des.Ui_Form):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self.img = cv.imread("frame10.jpg")
        #self.w, self.h  = QtGui.QPixmap.width(self.img), QtGui.QPixmap.height(self.img)
        self.mouseDrag = False
        self.ReadyBtn.clicked.connect(self.ending)
        self.pts = np.array([ [0,320], [520, 320], [520, 0], [0,0]])#bottom_left, bottom_right, top_right, top_left
        self.dst_pts = np.array([[50, 276], [618, 283], [458, 161], [181, 160]])
        self.mainStr = "Callibration"
        self.d_point = None
        #self.pixmap = None
        #self.e1 = threading.Event()
        #self.stopped = False
        #self.t1 = threading.Thread(target=self.delText, args=(5, self.e1))
        #self.daemon = True
        #self.t1.start()
        #self.btncheck = True
        self.init()

    def init(self):
        D = np.zeros((4))
        K = np.zeros((3, 3))
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
        h, w = self.img.shape[:2]
        map1, map2 = cv.fisheye.initUndistortRectifyMap(K, D, np.eye(3), K, (w, h), cv.CV_16SC2)
        self.img = cv.remap(self.img, map1, map2, interpolation=cv.INTER_LINEAR, borderMode=cv.BORDER_CONSTANT)
        self.showPicture()
            
    def ending(self):
        D = np.zeros((4))
        K = np.zeros((3, 3))
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
            'tl':self.pts[3],
            #'tl':(0,0),
            'tr':self.pts[2],
            'br':self.pts[1],
            'bl':self.pts[0],
            'bld':self.dst_pts[0],
            'brd':self.dst_pts[1],
            'trd':self.dst_pts[2],
            'tld':self.dst_pts[3]
            }
        try:
            with io.open('data_for_cam.yaml', 'w', encoding='utf8') as outfile:
                yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)
            print("Written!")
        except:
            print("Have a problem with data writing(")
        self.close()

    def showPicture(self):
        preview=np.copy(self.img)
        cv.polylines(preview,np.int32([self.dst_pts]),True,(0,0,255), 2) #отрисовываем линии
        pts = np.float32(self.pts.tolist())
        dst_pts = np.float32(self.dst_pts.tolist())
        h, mask = cv.findHomography(self.dst_pts, self.pts)
        image_size = (560, 370)
        warped = cv.warpPerspective(self.img, h, dsize = image_size, flags = cv.INTER_LINEAR) #переворачиваем фото в вертикальное
        #перемалываем формат openCV в Qt перевернутое изображение
        height, width, byteValue = warped.shape
        byteValue = byteValue * width
        self.mQImage = QtGui.QImage(warped, width, height, byteValue, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(self.mQImage.rgbSwapped())
        self.picture2.setPixmap(pixmap)
        #перемалываем формат openCV в Qt не перевернутое изображение
        height, width, byteValue = preview.shape
        byteValue = byteValue * width
        self.mQImage = QtGui.QImage(preview, width, height, byteValue, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap()
        pixmap.convertFromImage(self.mQImage.rgbSwapped())
        self.picture1.setPixmap(pixmap)


    def mousePressEvent(self, ev):
        if ev.button() == Qt.LeftButton:
            pos = ev.x()-10, ev.y()-60
            self.mouseDrag = True
            R1 = math.sqrt(math.pow(pos[0]-self.dst_pts[0][0], 2) + math.pow(pos[1]-self.dst_pts[0][1], 2))
            R2 = math.sqrt(math.pow(pos[0]-self.dst_pts[1][0], 2) + math.pow(pos[1]-self.dst_pts[1][1], 2))
            R3 = math.sqrt(math.pow(pos[0]-self.dst_pts[2][0], 2) + math.pow(pos[1]-self.dst_pts[2][1], 2))
            R4 = math.sqrt(math.pow(pos[0]-self.dst_pts[3][0], 2) + math.pow(pos[1]-self.dst_pts[3][1], 2))
            R = [R1, R2, R3, R4]
            Rm = min(R)
            for i in range(4):
                if R[i] == Rm:
                    self.dst_pts[i] = pos
                    self.d_point = i
            self.showPicture()

    def mouseMoveEvent(self, ev):
        if self.mouseDrag:
            self.dst_pts[self.d_point] = ev.x()-10, ev.y()-60
            self.showPicture()

    def mouseReleaseEvent(self, ev):
        self.dst_pts[self.d_point] = ev.x()-10, ev.y()-60
        self.mouseDrag = False
        self.showPicture()


    def closeEvent(self, event):
        reply = QtWidgets.QMessageBox.question(self, 'Message', "You've done?", QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)
        if reply == QtWidgets.QMessageBox.Yes:
            self.stopped = True
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()



def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication
    window = ExampleApp()  # Создаём объект класса ExampleApp
    window.show()  # Показываем окно
    app.exec_()  # и запускаем приложение

if __name__ == '__main__':  # Если мы запускаем файл напрямую, а не импортируем
    main()  # то запускаем функцию main()

