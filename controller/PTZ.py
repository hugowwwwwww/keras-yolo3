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
        """PTZ 的相機 """
        _imageDir = './image/'
        _fileName = 'output_'
        _fileCounter = 0
        _isVideo = True
        _isCapture = False

        def __init__(self, cameraId=0):
            """連接相機，出錯會回傳 false """
            try:
                self.cap = cv2.VideoCapture( cameraId )
            except:
                print( "Camera connect error." )
                return None

        def __del__(self):
            """關閉相機及所有 OpenCV 視窗 """
            self.cap.release()
            cv2.destroyAllWindows()

        def showVideo( self ):
            """開執行序顯示畫面 """
            self._isVideo = True
            t = threading.Thread(target = self._Camera__videoThread )
            t.start()

        def __videoThread( self ):
            """顯示畫面的執行序，用 isVideo 及 isCapture 控制 """
            while self._isVideo:
                ret , frame = self.cap.read()
                if not ret:
                    print('get frame error')
                    sys.exit()

                cv2.imshow('frame', frame )

                if self._isCapture: # 存檔
                    name = '%s%s%03d.jpg' % ( self._imageDir , self._fileName , self._fileCounter )
                    self._fileCounter += 1
                    cv2.imwrite( name  , frame )
                    self._isCapture = False

                wait = cv2.waitKey(1)
                if wait & 0xFF == ord('q'):
                    self._isVideo = False
                    print( 'type q and exit' )
                    sys.exit()

                if wait & 0xFF == ord('k'):
                    name = '%s%s%03d.jpg' % ( self._imageDir , self._fileName , self._fileCounter )
                    self._fileCounter += 1
                    cv2.imwrite( name  , frame )
                    print( 'type k and save an image... %s' % name )

        def getFrame( self ):
            """由外部呼叫，會回傳存圖的名稱 """
            self._isCapture = True
            while self._isCapture:
                pass
            name = '%s%03d.jpg' % (self._fileName, self._fileCounter-1 )
            return name

        def help( self ):
            """獲得文件說明 """
            d = PTZ.Camera.__dict__
            for k in d.keys():
                if( str( type( d[k] ) ) == "<class 'function'>" ):
                    print(  k  , '\n\t' , d[k].__doc__ )

    class Controller:

        # 是否定位
        _isPosFinish = True
        _isZoomFinsih = True
        _previousCommand = ''

        def __init__( self , ZOOOOM=0 , YYYY=0 , ZZZZ=0 , Port="COM3" , BaudRate=9600 ):
            """設定控制底座的初始狀況，並連接控制底座，不要用手轉控制底座！！ """
            # ZOOOOM: 聚焦程度 [0,65535]
            # YYYY  : 水平旋轉 [-2267,2267]
            # ZZZZ  : 上下旋轉 [-400,1200]
            # 紀錄初始化的位置
            self.initZOOOOM = ZOOOOM
            self.initZZZZ = ZZZZ
            self.initYYYY = YYYY

            # 紀錄當前位置
            self.ZOOOOM = ZOOOOM
            self.ZZZZ = ZZZZ
            self.YYYY = YYYY

            # 極限範圍
            self.ZOlimit = [ 0 , 65535 ]
            self.Ylimit = [ -1600 , 1600 ]
            self.Zlimit = [ -380 , 1180 ]

            # 當前轉向 (順或逆) (1,-1)
            self.Yclockwise = 1

            # 當前傾斜轉向 (上或下) (1,-1)
            self.Zclockwise = 1

            try:
                self.controller = serial.Serial( Port , BaudRate )
            except:
                print( "Controller connect error" )
                return None

        def __str__( self ):
            info = 'YYYY: {0:>4}  ZZZZ: {1:>4}  Zoom: {2:>5}'
            info = info.format( self.YYYY , self.ZZZZ , self.ZOOOOM )
            return info

        def resetPosition( self ):
            """回到初始位置 """
            # 使用的是相對位置，所以參數要這樣寫
            success = self.zoom( self.initZOOOOM - self.ZOOOOM  )
            if not success:
                print('zoom out range!')
                return False

            success = self.verticalMove( self.initZZZZ - self.ZZZZ )
            if not success:
                print('ZZZZ out range!')
                return False

            success = self.horizontalMove( self.initYYYY - self.YYYY )
            if not success:
                print('YYYY out range!')
                return False
            return True

        def zoom( self , d ):
            """控制鏡頭縮放，d>0 聚焦 """
            # 處理移動超出範圍
            if self.ZOOOOM + d < self.ZOlimit[0]:
                return False
            if self.ZOOOOM + d > self.ZOlimit[1]:
                return False

            # 移動在範圍內
            self.ZOOOOM += d

            # CAM_Zoom > Direct
            # command '8x010447'
            command = '81010447'

            # '0Z0Z0Z0Z'
            ZOstr = self._Controller__toHex( self.ZOOOOM )
            ZOstr = '0' + '0'.join( ZOstr )

            command += ZOstr
            command += 'FF'
            command = bytes.fromhex( command )

            self.controller.write( command )
            self._previousCommand = command
            return True


        def verticalMove( self , d ):
            """控制底座垂直轉動, d>0 向上 """
            # 處理移動超出範圍
            if self.ZZZZ + d < self.Zlimit[0]:
                return False
            if self.ZZZZ + d > self.Zlimit[1]:
                return False

            # 設定移動中
            self._isPosFinish = False
            # 移動在範圍內
            self.ZZZZ += d
            command = self._Controller__AP()
            self.controller.write( command )
            self._previousCommand = command
            # time.sleep(TimeDelay)
            return True

        def horizontalMove( self , d=0 ):
            """控制底座水平轉動, d>0 順時針 """
            # 處理移動超出範圍
            if self.YYYY + d < self.Ylimit[0]:
                return False
            if self.YYYY + d > self.Ylimit[1]:
                return False

            # 設定移動中
            self._isPosFinish = False
            # 移動在範圍內
            self.YYYY += d
            command = self._Controller__AP()
            self.controller.write( command )
            self._previousCommand = command
            # time.sleep(TimeDelay)
            return True


        def __AP( self ):
            """根據現在的狀況，求出絕對位置的指令 """
            # datasheet: Pan-titltDrive > AbsolutePostition
            # command '8x010602VVWW'
            command = '810106021414'
            
            Ystr = self._Controller__toHex( self.YYYY )
            Zstr = self._Controller__toHex( self.ZZZZ )
            # '0Y0Y0Y0Y'
            Ystr = '0' + '0'.join( Ystr )
            
            # '0Z0Z0Z0Z'
            Zstr = '0' + '0'.join( Zstr )
            command += Ystr + Zstr + 'FF'
            return bytes.fromhex( command )

        def __toHex( self , n ):
            """將數字轉換成四位hex碼(用於 YYYY, ZZZZ) """
            if n < 0:
                n = 65536 + n
            hexStr = hex(n)
            hexStr = hexStr[2:]
            hexStr = '{:0>4}'.format( hexStr )
            return hexStr

        def __toDec( self , byteStr ):
            """將八位 bytes string (0Y0Y0Y0Y) 轉成 Dec """
            numArr = [ c for c in byteStr]

            n = 0
            for i in range(3,-1,-1):
                n += numArr[i] * (16**i)
            return n

        def __clearBuffer(self):
            """清空控制底座回傳的封包 """
            command = '88010001FF'
            command = bytes.fromhex( command )

            self.controller.write( command )

            while True:
                bStr = b''
                while True:
                    b = self.controller.read()
                    bStr += b
                    if b == b'\xff':
                        break
                if bStr == command:
                    break

        def isFinish( self ):
           
            """
            if not self._isZoomFinsih:
                pass
                if ...
                    self._isZoomFinsih
            """

            if not self._isPosFinish:
                # 清空暫存
                self._Controller__clearBuffer()

                # 寫入查詢指令
                command = '81090612FF'
                command = bytes.fromhex( command )
                self.controller.write( command )
                
                # 接收回傳
                bStr = self.controller.read(11)

                # 轉換成數字
                Ynum = self._Controller__toDec( bStr[2:6] )
                Znum = self._Controller__toDec( bStr[7:11] )

                if self.YYYY == Ynum and self.ZZZZ == Znum:
                    self._isPosFinish = True

                print( Ynum )

            if self._isZoomFinsih and self._isPosFinish:
                return True
            else:
                self.controller.write( self._previousCommand )
                return False



if __name__ == '__main__':
    # ca.help()
    # ca = PTZ.Camera()
    # ca.showVideo()

    co = PTZ.Controller()

    co.resetPosition()
    time.sleep(2)
    co._Controller__clearBuffer()
    co.horizontalMove( 1200 )

    while True:
        flag = co.isFinish()
        print( flag )
        if flag:
            break



