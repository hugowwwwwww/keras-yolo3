import socket               # 导入 socket 模块
import cv2

def connect():
    Port = 9006                    # 設定的 Port ，與 run.bat 同步

    s = socket.socket()         # 建立 socket 物件
    host = socket.gethostname() # 獲得電腦主機名稱
    
    s.connect((host, Port))     # 連接到 9006 Port
    return s


s = connect()


# current /controller/
image_dir = './image/'

cap = cv2.VideoCapture(1)
cc = 0
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

  if wait & 0xFF == ord('k'):
    #cv2.resize(frame,640,480)
    file_name = 'output_%03d.jpg'%cc
    cv2.imwrite( image_dir+file_name ,frame)
    cc += 1
    print('snapshot complete... pass image location...')
    
    s.send( file_name.encode('utf-8') )
    data = s.recv(1024) # 等待
    print( 'get data from server ----------' )


    data = data.decode()

    targets = []
    rows = data.split('\n')
    for row in rows:
        targets.append( row.split(',') )


    category = [ 'car' , 'License Plate']


    del targets[0]
    if len(targets) == 0:
        continue
    else:
        idx = 0
        max_acc = float(targets[0][1])

        for i in range(1,len(targets)):
            if float( targets[i][1] ) > max_acc:
                max_acc = targets[i][1]
                idx = i

        coord = targets[idx]
        del coord[0:2] # remove category and acc
        coord = list( map( int , coord ) )
        # 左上右下




        print(coord)





s.close()

# 釋放攝影機
cap.release()

# 關閉所有 OpenCV 視窗
cv2.destroyAllWindows()
