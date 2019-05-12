docker stop d9010
docker rm d9010
nvidia-docker run -dit -p 9010:8888 -p 9012:6006 -p 9014:9006 --name d9010 -v /home/hugo/yolo:/root --ipc=host ufoym/deepo:all-jupyter-py36-cu90 jupyter notebook --no-browser --ip=0.0.0.0 --allow-root --NotebookApp.token= --notebook-dir='/root'
