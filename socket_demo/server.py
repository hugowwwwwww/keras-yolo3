# server
import socket

Port = 9008					# 設定的 Port ，與 run.bat 同步

s = socket.socket()         # 建立 socket 物件
host = socket.gethostname() # 獲得電腦主機名稱
s.bind((host, Port))        # 監聽 9006 Port
 
s.listen(3)                 # 開始監聽，並設置最大監聽數量
while True:	
    conn,addr = s.accept()  # 建立與客戶端的連接
    print( "connected from " + str(addr) )

    msg = "hello"+ str(addr)
    conn.send( msg.encode('utf-8')    )

    data = conn.recv(1024)
    print('recive:' , data.decode() )
    
    conn.close()                # 关闭连接