docker stop d9002
docker rm d9002
docker run -dit -p 9002:8888 -p 9004:6006 -p 9006:9006 --name d9002  -v C:\Users\hugo\Desktop\d9002:/root  --ipc=host ufoym/deepo:all-py36-jupyter-cpu jupyter notebook --no-browser --ip=0.0.0.0 --allow-root --NotebookApp.token= --notebook-dir='/root'
