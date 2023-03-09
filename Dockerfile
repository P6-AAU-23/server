FROM python:3

WORKDIR /usr/src/app

# opencv-python dependencies
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]
