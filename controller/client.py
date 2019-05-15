import socket               # 导入 socket 模块
import cv2
import serial
import time

def connect():
    Port = 9006                    # 設定的 Port ，與 run.bat 同步
    
    s = socket.socket()         # 建立 socket 物件
    host = socket.gethostname() # 獲得電腦主機名稱
    
    s.connect(('140.115.26.67', 9014))     # 連接到 9006 Port
    return s


s = connect()


def toHex( n ):
    if n < 0:
        n = 65536 + n
    hex_str = hex(n)
    hex_str = hex_str[2:]
    while len(hex_str) < 4:
        hex_str = '0' + hex_str
    return hex_str

def AP(  YYYY , ZZZZ ):
    Zpadding = 20
    ZDlim = -400 + Zpadding  # 下
    ZUlim = 1200 - Zpadding  # 上
    if ZZZZ < ZDlim:
        ZZZZ = ZDlim
    if ZZZZ > ZUlim:
        ZZZZ = ZUlim
    
    Ypadding = 67
    YRlim = -2267 + Ypadding # 逆時針
    YLlim = 2267 - Ypadding  # 順時針
    
    if YYYY < YRlim:
        YYYY = YRlim
    if YYYY > YLlim:
        YYYY = YLlim
    
    command = '810106021817'
    
    Ystr = toHex(YYYY)
    Zstr = toHex(ZZZZ)
    for i in range(4):
        command += '0' + Ystr[i]
    for i in range(4):
        command += '0' + Zstr[i]
    command += 'FF'
    return bytes.fromhex( command )

def Zoom( OOOO ):
    command = '81010447'
    Ostr = toHex(OOOO)
    for i in range(4):
        command += '0'+Ostr[i]
    command += 'FF'
    return bytes.fromhex( command )

# current /controller/
image_dir = './image/'

cap = cv2.VideoCapture(0)
cc = 0

# 連接鏡頭
ser=serial.Serial("COM3",9600)
ZZZZ = 140
YYYY = 200
initOOOO = 0
OOOO = initOOOO
Zoom_counter = 0
isCounter = False
ro = True # 反 -Y 轉
Zdec = -30
ser.write( AP(YYYY,ZZZZ) )
ser.write( Zoom(OOOO) )
time.sleep(2)

YRange = 300

while(True):
  # 從攝影機擷取一張影像
  ret, frame = cap.read()

  # 顯示圖片
  cv2.imshow('frame', frame)
  
  # 若按下 q 鍵則離開迴圈
  wait=cv2.waitKey(1)
  if wait & 0xFF == ord('q'):
    s.send( 'exit'.encode('utf-8') )
    break

  if True or  wait & 0xFF == ord('k'):
    #cv2.resize(frame,640,480)
    file_name = 'output_%03d.jpg'%cc
    cv2.imwrite( image_dir+file_name ,frame)

    print()
    print( '[%03d] '%cc , end='' )
    print( "YYYY: %d  ZZZZ: %d  " % (YYYY,ZZZZ) , end=''  )
   
    cc += 1
    # print('snapshot complete... pass image location...'+file_name)    
    s.send( file_name.encode('utf-8') )

    data = s.recv(1024) # 等待
    # print( data.decode() )

    with open( image_dir+file_name , 'rb') as f:
        for data in f:
            s.send(data)
    s.close()
    s = connect()

    data = s.recv(1024) # 等待

    # print( 'get data from server ----------' )


    data = data.decode()

    arr = []
    rows = data.split('\n')
    for row in rows:
        arr.append( row.split(',') )

    del arr[0]

    category = [ 'car' , 'License Plate']

    targets = []
    for row in arr:
        if row[0] == category[0]:
            targets.append(row)


    if len(targets) == 0:
        r_step_len = 12
        isDec = False
        if ro and YYYY >= -800:
            YYYY -= r_step_len
        elif ro and YYYY < -800:
            ro = False
            ZZZZ += Zdec

        if not ro and YYYY <= 800:
            YYYY += r_step_len
        elif not ro and YYYY > 800:
            ro = True
            ZZZZ += Zdec

        if ZZZZ < -300:
            Zdec = abs(Zdec)
        if ZZZZ > 1100:
            Zdec = -abs(Zdec)


        ser.write( AP(YYYY,ZZZZ) )

        continue
    else:
        idx = 0
        max_acc = float(targets[0][1])

        for i in range(1,len(targets)):
            # print(targets[i][1]   )
            if float( targets[i][1] ) > max_acc:
                max_acc = float(targets[i][1])
                idx = i

        if max_acc < 0.7:

            r_step_len = 12
            isDec = False
            if ro and YYYY >= -800:
                YYYY -= r_step_len
            elif ro and YYYY < -800:
                ro = False
                ZZZZ += Zdec

            if not ro and YYYY <= 800:
                YYYY += r_step_len
            elif not ro and YYYY > 800:
                ro = True
                ZZZZ += Zdec

            if ZZZZ < -300:
                Zdec = abs(Zdec)
            if ZZZZ > 1100:
                Zdec = -abs(Zdec)


            ser.write( AP(YYYY,ZZZZ) )

        else:


            coord = targets[idx]
            del coord[0:2] # remove category and acc
            coord = list( map( int , coord ) )

            print( "acc: %.3f   " % max_acc , end=''  )
            print(coord , end='')
            # 左上右下

            cx = (coord[0] + coord[2])/2
            cy = (coord[1] + coord[3])/2

            mx = 320
            my = 240
            err = 20

            step_len = 5

            isMove = False

            if cx > mx+err:
                YYYY += step_len # 逆
                isMove = True
            if cx < mx-err:
                YYYY -= step_len # 順
                isMove = True
            if cy > my+err:
                ZZZZ -= round(step_len*0.75) # 上
                isMove = True
            if cy < my-err:
                ZZZZ += round(step_len*0.75) # 下
                isMove = True

            if isMove:
                ser.write( AP(YYYY,ZZZZ) )
                if Zoom_counter != 0:
                    OOOO -= Zoom_counter*Zoom_step_len
                    Zoom_counter = 0
                    time.sleep(0.1)
                    ser.write( Zoom(OOOO) )

            else:
                zoom_y_padding = 20
                Zoom_x_padding = 30
                if OOOO < 65535: # 左上右下
                    isZoom = True
                    if coord[0] < Zoom_x_padding:
                        isZoom = False
                    if coord[2] > 640-Zoom_x_padding:
                        isZoom = False
                    if coord[1] < zoom_y_padding:
                        isZoom = False
                    if coord[3] > 480-zoom_y_padding:
                        isZoom = False

                    Zoom_step_len = 100
                    print( '  isZoom: ' , isZoom , end='' )
                    if isZoom:
                        Zoom_counter = 0
                        isCounter = False
                        OOOO += Zoom_step_len
                        ser.write( Zoom(OOOO) )
                    else:
                        Zoom_counter += 1

                    if Zoom_counter > 5:
                        Zoom_counter = 0
                        print('  ng ' , end='')
                        OOOO = initOOOO

                        ser.write( Zoom(OOOO) )
                        for i in range(15):
                            print( i , "...")
                            time.sleep(0.1)

                        if ro and YYYY >= -800:
                            YYYY -= 200#(coord[2]-coord[0])*(coord[3]-coord[1])
                        elif ro and YYYY < -800:
                            ro = False

                        if not ro and YYYY <= 800:
                            YYYY += 200#(coord[2])
                        elif not ro and YYYY > 800:
                            ro = True
                        ser.write( AP(YYYY,ZZZZ) )

        time.sleep(0.1)


s.close()

ser.close()

# 釋放攝影機
cap.release()

# 關閉所有 OpenCV 視窗
cv2.destroyAllWindows()
