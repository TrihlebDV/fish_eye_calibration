#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import cv2
import numpy as np
import threading
import gi
from gi.repository import GObject
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import psutil
import os
import math

#библиотеки СКТБ
import rpicam

CHECKERBOARD = (9, 7)

#настройки видеопотока
#FORMAT = rpicam.FORMAT_H264
FORMAT = rpicam.FORMAT_MJPEG
WIDTH, HEIGHT = 640, 360
RESOLUTION = (WIDTH, HEIGHT)
FRAMERATE = 30

#сетевые параметры
#IP = '192.168.42.50' #пульт
IP = '10.42.0.1' #пульт
RTP_PORT = 5000 #порт отправки RTP видео
DEBUG_PORT = 8000 #порт отправки отладочных кадров XML-RPC
CONTROL_PORT = 9000 #порт XML-RPC управления роботом

#Чувтвительность алгоритма определения линии
SENSITIVITY = 65

#
BASE_SPEED = 35

dirkof = 32 #кэфицент при изменении курса.

cameraPos = False #False - смотрим прямо, True - смотрим вниз

class LineFollow(threading.Thread):
    #камера источник кадров, ширина фрейма в кадре, выстота фрейма в кадре, привязка по нижней границе
    def __init__(self, camera, width, height, debugClient):
        threading.Thread.__init__(self)
        self.oldDirection = True #True - видел линию справа, False - видел линию слева
        self.lineLost = False
        self.h = None
        self.map1 = None
        self.map2 = None
        self.checkAutoMode = [0,0]
        self.daemon = True
        self.speedCount = 0
        self._stopped = threading.Event() #событие для остановки потока
        self.camera = camera
        self._frame = None
        self._check = False
        self.automat = False
        self.debug = False
        self.sensitivity = 127 #чувствительность алгоритма определения линии (0..255)
        self.width = width
        if width > WIDTH:     # проверить нужно ли вообще
            self.width = WIDTH
        self.height = height
        if height > HEIGHT:
            self.height = HEIGHT
        self._top = HEIGHT - height #верхняя точка среза
        self._left = (WIDTH - width)//2 #левая точка среза
        self._right = self._left + width #правая точка среза
        self._bottom = HEIGHT #нижняя точка среза
        self._newFrameEvent = threading.Event() #событие для контроля поступления кадров
        #отладочный сервер
        self.debugClient = debugClient
        
    def run(self):
        global sideCheck
        print('Line follow started, sensitivity: %d' % self.sensitivity)
        count = 0
        fname = 'img'
        while not self._stopped.is_set():
            self.camera.frameRequest() #отправил запрос на новый кадр
            self._newFrameEvent.wait() #ждем появления нового кадра
            if not (self._frame is None): #если кадр есть
                if self.debug:
                    gray = cv2.cvtColor(self._frame, cv2.COLOR_BGR2GRAY)
                    ret, corners = cv2.findChessboardCorners(gray, CHECKERBOARD, cv2.CALIB_CB_ADAPTIVE_THRESH+cv2.CALIB_CB_FAST_CHECK+cv2.CALIB_CB_NORMALIZE_IMAGE)
                    img = gray.copy()
                    cv2.drawChessboardCorners(img, img.shape[:2], corners, ret)
                    if ret: print("Yeah!!")
                    else: print("nothing found")
                    if self._check:
                        fname = fname + str(count) + ".jpg"
                        cv2.imwrite(fname, gray)
                        count += 1
                    # берем нижнюю часть кадра
                    #crop = self._frame[self._top:self._bottom, self._left:self._right]    #обрезаем кадр

                            
                    res, img = cv2.imencode('.jpg', img) #преобразовал картинку в массив
                    if res:
                        try:
                            self.debugClient.drawCvFrame(img.tobytes()) #заслал картинку
                        except Exception as err:
                            print('Fault code:', err.faultCode)
                            print('Message   :', err.faultString)
                    time.sleep(2)
                            
            self._newFrameEvent.clear() #сбрасываем событие

        print('Line follow stopped')

    def stop(self): #остановка потока
        self._stopped.set()
        if not self._newFrameEvent.is_set(): #если кадр не обрабатывается
            self._frame = None
            self._newFrameEvent.set() 
        self.join()

    def setFrame(self, frame): #задание нового кадра для обработки
        if not self._newFrameEvent.is_set(): #если обработчик готов принять новый кадр
            self._frame = frame
            self._newFrameEvent.set() #задали событие
        return self._newFrameEvent.is_set()

        
def onFrameCallback(frame): #обработчик события 'получен кадр'
    lineFollow.setFrame(frame) #задали новый кадр

def check():
    lineFollow._check = not lineFollow._check
    return 0

def Debug():
    lineFollow.debug =  not lineFollow.debug
    if(lineFollow.debug == True):
        return 1
    else:
        return 0

print('Start program')



assert rpicam.checkCamera(), 'Raspberry Pi camera not found'
print('Raspberry Pi camera found')

# Получаем свой IP адрес
ip = rpicam.getIP()
assert ip != '', 'Invalid IP address'
print('Robot IP address: %s' % ip)

print('OpenCV version: %s' % cv2.__version__)

#нужно для корректной работы системы
GObject.threads_init()
mainloop = GObject.MainLoop()

#видеопоток с камеры робота    
robotCamStreamer = rpicam.RPiCamStreamer(FORMAT, RESOLUTION, FRAMERATE, (IP, RTP_PORT), onFrameCallback)
#robotCamStreamer = rpicam.RPiCamStreamer(FORMAT, RESOLUTION, FRAMERATE, (IP, RTP_PORT))
#robotCamStreamer.setFlip(False, True)
robotCamStreamer.setRotation(180)
robotCamStreamer.start()


        
# XML-RPC сервер управления в отдельном потоке
serverControl = SimpleXMLRPCServer((ip, CONTROL_PORT)) #запуск XMLRPC сервера
serverControl.logRequests = False #оключаем логирование
print('Control XML-RPC server listening on %s:%d' % (ip, CONTROL_PORT))


serverControl.register_function(Debug)
serverControl.register_function(check)


#запускаем сервер в отдельном потоке
serverControlThread = threading.Thread(target = serverControl.serve_forever)
serverControlThread.daemon = True
serverControlThread.start()

#XML-RPC клиент для запуска отладочных процедур
debugClient = xmlrpc.client.ServerProxy('http://%s:%d' % (IP, DEBUG_PORT))

#контроль линии    
lineFollow = LineFollow(robotCamStreamer, int(WIDTH/7*4), int(HEIGHT/2), debugClient)
lineFollow.debug = False
lineFollow.sensitivity = SENSITIVITY
lineFollow.start()

#главный цикл программы    
try:
    mainloop.run()
except (KeyboardInterrupt, SystemExit):
    print('Ctrl+C pressed')

#останов сервера
serverControl.server_close()

#останов контроля линии
lineFollow.stop()

print('End program')


