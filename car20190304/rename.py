import os,sys
now_dir=os.getcwd()
fname=os.listdir(now_dir)
count=1
for file in fname:
    if "jpg" in file:
        print(os.path.join(now_dir, file))
        os.rename(os.path.join(now_dir,file),os.path.join(now_dir,str(count)+'.jpg'))
        count+=1