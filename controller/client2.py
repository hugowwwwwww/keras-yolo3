import socket
import cv2
import serial
import time
import sys

TimeDelay = 0.05

class PTZ:
    def __init__( self , ZOOOOM , YYYY , ZZZZ , cameraInfo , controllerInfo ):
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
        self.Zlimit = [ -380 , 1180 ]
        self.Ylimit = [ -400 , 400 ] #2230
        # 當前轉向 (順或逆) (1,-1)
        self.Yclockwise = 1
        # 當前傾斜轉向 (上或下) (1,-1)
        self.Zclockwise = -1

        # 連線到提供顯卡的機器
        self.client = None
        self.waitServerLock = False
        # PTZ 的相機
        self.camera = None
        # PTZ 的控制底座
        self.controller = None

        # 連線到 PTZ 的相機
        # 陣列內 None 的數量要和參數數量一樣
        
        if cameraInfo == None:
            cameraInfo = [ None ]
        success = self.connectCamera( *cameraInfo )
        if not success:
            print('connect camera error!')
            sys.exit()

        # 連線到 PTZ 的控制底座
        # 陣列內 None 的數量要和參數數量一樣
        if controllerInfo == None:
            controllerInfo = [ None , None ]
        
        success = self.connectController( *controllerInfo )
        
        if not success:
            print('connect controller error!')
            sys.exit()

        success = self.resetPosition()
        if not success:
            print('reset position error!' )
            sys.exit()

        print( 'PTZ is ready' )

    def __del__( self ):
        if self.client != None:
            pass
        if self.camera != None:
            self.camera.release()
        # 關閉所有 OpenCV 視窗
        cv2.destroyAllWindows()

        if self.controller != None:
            self.controller.close()



    def __str__( self ):
        info = 'YYYY: {0:>4}  ZZZZ: {1:>4}  Zoom: {2:>5}'
        info = info.format( self.YYYY , self.ZZZZ , self.ZOOOOM )
        return info

    def Rule( data ):
        pass
        '''
        if ... Zoom
        if ... YYYY
        if ... ZZZZ
        '''


    #----------------- connect server
    def connectServer( self , host , port ):
        self.client = socket.socket()
        if host == None:
            host = socket.gethostname()
        if port == None:
            port = 9006

        self.client.connect( ( host , port ) )

    def __sendData( self , data ):
        s.send( data.encode('utf-8') )

    def sendFile( self , fileName ):
        pass
        '''
        send 檔案大小
        recv 檔案大小
        send 傳送檔案
        recv 處理完的座標
        '''

    #----------------- connect camera
    def connectCamera(self , cameraId ):
        if cameraId == None:
            cameraId = 0
        print(cameraId)
        try:
            self.camera = cv2.VideoCapture(0)
            return True
        except:
            return False

    def showVideo( self ):
        while True:
            frame = self._PTZ__getFrame()
            wait=cv2.waitKey(1)
            if wait & 0xFF == ord('q'):
                sys.exit()
            cv2.imshow('frame', frame )

        # 開執行序出去


    def __getFrame( self ):
        ret, frame = self.camera.read()
        if not ret:
            print('get frame error')
            sys.exit()
        else:
            return frame

    #----------------- connect controller
    def connectController( self , port , baudRate ):
        if port == None:
            port = "COM3"
        if baudRate == None:
            baudRate = 9600

        try:
            self.controller = serial.Serial( port , baudRate )
            return True
        except:
            return False

    def resetPosition( self ):
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

    def regularRotation(self , speed ):
        Yspeed , Zspeed = speed
        # 左右移動
        success = self.horizontalMove( self.Yclockwise * Yspeed )
        # 轉向
        if not success:
            # 上下移動
            success = self.verticalMove( self.Zclockwise * Zspeed )
            # 轉向
            if not success:
                self.Zclockwise = -self.Zclockwise
                success = self.verticalMove( self.Zclockwise * Zspeed )
                # 應該不會出現這種情況
                if not success:
                    print( 'regularRotation for Z error!' )
                    sys.exit()

            # 繼續左右移動
            self.Yclockwise = -self.Yclockwise
            success = self.horizontalMove( self.Yclockwise * Yspeed )

            # 應該不會出現這種情況
            if not success:
                print( 'regularRotation for Y error!' )
                sys.exit()

        frame = self._PTZ__getFrame()
        cv2.imshow('frame', frame )

        wait = cv2.waitKey(1)
        if wait & 0xFF == ord('q'):
            sys.exit()

    def zoom( self , d ):
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
        ZOstr = self._PTZ__toHex( self.ZOOOOM )
        ZOstr = '0' + '0'.join( ZOstr )

        command += 'FF'
        command = bytes.fromhex( command )

        self.controller.write( command )
        return True


    def verticalMove( self , d ):
        # 處理移動超出範圍
        if self.ZZZZ + d < self.Zlimit[0]:
            return False
        if self.ZZZZ + d > self.Zlimit[1]:
            return False

        # 移動在範圍內
        self.ZZZZ += d
        self.controller.write( self._PTZ__AP() )
        time.sleep(TimeDelay)
        return True

    def horizontalMove( self , d ):
        # 處理移動超出範圍
        if self.YYYY + d < self.Ylimit[0]:
            return False
        if self.YYYY + d > self.Ylimit[1]:
            return False

        # 移動在範圍內
        self.YYYY += d
        self.controller.write( self._PTZ__AP() )
        time.sleep(TimeDelay)
        return True

    def __AP( self ):
        # Pan-titltDrive > AbsolutePostition
        # command '8x010602VVWW'
        command = '810106021414'
        
        Ystr = self._PTZ__toHex( self.YYYY )
        Zstr = self._PTZ__toHex( self.ZZZZ )

        # '0Y0Y0Y0Y'
        Ystr = '0' + '0'.join( Ystr )
        
        # '0Z0Z0Z0Z'
        Zstr = '0' + '0'.join( Zstr )

        command += Ystr + Zstr + 'FF'
        return bytes.fromhex( command )

    def __toHex( self , n ):
        # YYYY , ZZZZ 的處理
        if n < 0:
            n = 65536 + n

        hexStr = hex(n)
        hexStr = hexStr[2:]
        hexStr = '{:0>4}'.format( hexStr )

        return hexStr


ptz = PTZ( 0 , 0 ,0 , None , None )

while True:
    s = 1
    ptz.regularRotation( [s,s] )
    print( ptz , end='\r')

print(  )
del ptz
