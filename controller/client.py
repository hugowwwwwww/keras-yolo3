import socket               # 导入 socket 模块
import cv2
import serial
import time

def connect():
    Port = 9006                    # 設定的 Port ，與 run.bat 同步

    s = socket.socket()         # 建立 socket 物件
    host = socket.gethostname() # 獲得電腦主機名稱
    
    s.connect((host, Port))     # 連接到 9006 Port
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
    print(command)
    return bytes.fromhex( command )

# current /controller/
image_dir = './image/'

cap = cv2.VideoCapture(1)
cc = 0

# 連接鏡頭
ser=serial.Serial("COM3",9600)
ZZZZ = 200
YYYY = 0
ro = True # 反 -Y 轉
Zdec = 30
ser.write( AP(YYYY,ZZZZ) )

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
    cc += 1
    print('snapshot complete... pass image location...')
    
    s.send( file_name.encode('utf-8') )
    data = s.recv(1024) # 等待
    print( 'get data from server ----------' )


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
        r_step_len = 100
        if ro and YYYY >= -800:
            YYYY -= r_step_len
        else:
            ro = False
            ZZZZ -= Zdec

        if not ro and YYYY <= 800:
            YYYY += r_step_len
        else:
            ro = True
            ZZZZ -= Zdec


        ser.write( AP(YYYY,ZZZZ) )

        continue
    else:
        idx = 0
        max_acc = float(targets[0][1])

        for i in range(1,len(targets)):
            print(targets[i][1]   )
            if float( targets[i][1] ) > max_acc:
                max_acc = float(targets[i][1])
                idx = i

        if max_acc < 0.8:

            r_step_len = 100
            if ro and YYYY >= -600:
                YYYY -= r_step_len
            else:
                ro = False

            if not ro and YYYY <= 600:
                YYYY += r_step_len
            else:
                ro = True
            ser.write( AP(YYYY,ZZZZ) )


        coord = targets[idx]
        del coord[0:2] # remove category and acc
        coord = list( map( int , coord ) )
        # 左上右下

        cx = (coord[0] + coord[2])/2
        cy = (coord[1] + coord[3])/2

        mx = 320
        my = 240
        err = 50

        step_len = 20

        if cx > mx+err:
            YYYY += step_len # 逆
        if cx < mx-err:
            YYYY -= step_len # 順
        if cy > my+err:
            ZZZZ -= step_len # 上
        if cy < my-err:
            ZZZZ += step_len # 下

        ser.write( AP(YYYY,ZZZZ) )
        time.sleep(0.2)


        print(coord)



s.close()

ser.close()

# 釋放攝影機
cap.release()

# 關閉所有 OpenCV 視窗
cv2.destroyAllWindows()
