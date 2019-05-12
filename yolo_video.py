import sys
import argparse
from yolo import YOLO, detect_video
from PIL import Image
import cv2
import os
import socket


'''
def detect_img(yolo):
    while True:
        img = input('Input image filename:')
        try:
            image = Image.open(img)
        except:
            print('Open Error! Try again!')
            continue
        else:
            r_image = yolo.detect_image(image)
            r_image.show()
            r_image.save('./image1227/new516.jpg')
    yolo.close_session()
'''
def detect_img(yolo):

    # 與 run.bat 的 Port 同步，要出去 docker 的 Port

    Port = 9006                 # 設定的 Port ，與 run.bat 同步

    s = socket.socket()         # 建立 socket 物件
    host = socket.gethostname() # 獲得電腦主機名稱
    s.bind((host, Port))        # 監聽 9006 Port
     
    s.listen(3)                 # 開始監聽，並設置最大監聽數量
    print( "Waiting ..." )
    while True: 
        conn,addr = s.accept()  # 建立與客戶端的連接
        print( "connected from " + str(addr) )

        msg = "hello"+ str(addr)
        conn.send( msg.encode('utf-8')    )

        data = conn.recv(1024)
        print('recive:' , data.decode() )
        
        conn.close()                # 關閉連接

'''
    pic='./car20190304'
    goal_dir='./predict_new_2019'
    files=os.listdir(pic)
    for file in files:
        try:
            image = Image.open(pic+'/'+file)
        except:
            print('Open Error! Try again!')
            continue
        else:
            r_image = yolo.detect_image(image)
            r_image.show()
            r_image.save(goal_dir+'/'+file)
    yolo.close_session()      

    FLAGS = None
'''
if __name__ == '__main__':
    # class YOLO defines the default value, so suppress any default here
    parser = argparse.ArgumentParser(argument_default=argparse.SUPPRESS)
    '''
    Command line options
    '''
    parser.add_argument(
        '--model', type=str,
        help='path to model weight file, default ' + YOLO.get_defaults("model_path")
    )

    parser.add_argument(
        '--anchors', type=str,
        help='path to anchor definitions, default ' + YOLO.get_defaults("anchors_path")
    )

    parser.add_argument(
        '--classes', type=str,
        help='path to class definitions, default ' + YOLO.get_defaults("classes_path")
    )

    parser.add_argument(
        '--gpu_num', type=int,
        help='Number of GPU to use, default ' + str(YOLO.get_defaults("gpu_num"))
    )

    parser.add_argument(
        '--image', default=False, action="store_true",
        help='Image detection mode, will ignore all positional arguments'
    )
    '''
    Command line positional arguments -- for video detection mode
    '''
    parser.add_argument(
        "--input", nargs='?', type=str,required=False,default='./path2your_video',
        help = "Video input path"
    )

    parser.add_argument(
        "--output", nargs='?', type=str, default="",
        help = "[Optional] Video output path"
    )

    FLAGS = parser.parse_args()

    if FLAGS.image:
        """
        Image detection mode, disregard any remaining command line arguments
        """
        print("Image detection mode")
        if "input" in FLAGS:
            print(" Ignoring remaining command line arguments: " + FLAGS.input + "," + FLAGS.output)
        detect_img(YOLO(**vars(FLAGS)))
    elif "input" in FLAGS:
        detect_video(YOLO(**vars(FLAGS)), FLAGS.input, FLAGS.output)
    else:
        print("Must specify at least video_input_path.  See usage with --help.")
