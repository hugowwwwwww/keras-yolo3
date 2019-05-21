import socket
import cv2
import serial
import time
import sys
import threading



class PTZ:
    """ PTZ 的相機和控制底座 """

    def __init__ (self , cameraInfo=None , controllerInfo=None  ):
        self.camera = None


        #self.controller = PTZ.Controller()



    class Camera:
        """ PTZ 的相機 """
        imageDir = './image/'
        fileName = 'output_'
        fileCounter = 0
        _isVideo = True
        _isCapture = False

        def __init__(self, cameraId=0):
            """ 連接相機，出錯會回傳 false """
            try:
                self.cap = cv2.VideoCapture( cameraId )
            except:
                print( "Camera connect error." )
                return None

        def __del__(self):
            # 關閉相機及所有 OpenCV 視窗
            self.cap.release()
            cv2.destroyAllWindows()

        def showVideo( self ):
            """ 開執行序顯示畫面 """
            self._isVideo = True
            t = threading.Thread(target = self._Camera__videoThread )
            t.start()

        def __videoThread( self ):
            """ 顯示畫面的執行序，用 isVideo 及 isCapture 控制 """
            while self._isVideo:
                ret , frame = self.cap.read()
                if not ret:
                    print('get frame error')
                    sys.exit()

                cv2.imshow('frame', frame )

                if self._isCapture: # 存檔
                    name = '%s%s%03d.jpg' % ( self.imageDir , self.fileName , self.fileCounter )
                    self.fileCounter += 1
                    cv2.imwrite( name  , frame )
                    self._isCapture = False

                wait = cv2.waitKey(1)
                if wait & 0xFF == ord('q'):
                    self._isVideo = False
                    print( 'type q and exit' )
                    sys.exit()

                if wait & 0xFF == ord('k'):
                    name = '%s%s%03d.jpg' % ( self.imageDir , self.fileName , self.fileCounter )
                    self.fileCounter += 1
                    cv2.imwrite( name  , frame )
                    print( 'type k and save an image... %s' % name )

        def getFrame( self ):
            self._isCapture = True
            while self._isCapture:
                pass
            name = '%s%03d.jpg' % (self.fileName, self.fileCounter-1 )
            return name

    class Controller:
        pass


if __name__ == '__main__':
    ca = PTZ.Camera()
    ca.showVideo()


    while True:
        time.sleep(3)
        print( ca.getFrame() )