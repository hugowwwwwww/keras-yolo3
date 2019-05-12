import socket               # 导入 socket 模块


def connect():
	Port = 9006					# 設定的 Port ，與 run.bat 同步

	s = socket.socket()         # 建立 socket 物件
	host = socket.gethostname() # 獲得電腦主機名稱
	
	s.connect((host, Port))     # 連接到 9006 Port
	return s



msg = input("open file > ")
s.send( msg.encode('utf-8') )

s.close()