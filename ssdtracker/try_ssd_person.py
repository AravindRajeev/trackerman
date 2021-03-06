# -*- coding: utf-8 -*-
"""try_ssd_person.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1DhHZXMBrd6GG6WgauTr62AaVl-LGBQN9
"""

!pip install scipy filterpy==1.4.1 numba==0.38.1 scikit-image==0.14.0 scikit-learn==0.19.1 numpy==1.15.4

import torch
from torch.autograd import Variable
import cv2
from data import BaseTransform, VOC_CLASSES as labelmap
from ssd import build_ssd
import imageio
import matplotlib.pyplot as plt
import time
import numpy as np
import sys
from sort import *

# %matplotlib inline

device = torch.device("cuda")
torch.set_default_tensor_type('torch.cuda.FloatTensor')

net = build_ssd('test',300,2).cuda()
net.load_state_dict(torch.load('weights/ssd_person.pth'))

transform = BaseTransform(net.size, (104/256.0, 117/256.0, 123/256.0))

COLORS = np.random.rand(32,3)*256
FONT = cv2.FONT_HERSHEY_PLAIN
count = 0

def process_image(image,mot_tracker):
    height, width = image.shape[:2]
    x = torch.from_numpy(transform(image)[0]).permute(2, 0, 1)
    x = Variable(x.unsqueeze(0))
    x = x.cuda()
    
    y = net(x)
    
    detections = y.data
    scale = torch.Tensor([width-width*.025, height-height*.05, width+width*.025, height+height*.05])
    
    allbox = []
    for i in range(detections.size(2)):
        if detections[0, 1, i, 0] >= .5:
            pt = (detections[0, 1, i, 1:] * scale).cpu().numpy()
            bbox = np.append(pt, (detections[0, 1, i, 0]).cpu().numpy())
            allbox.append(bbox)
    
    allbbox = np.array(allbox)
    track_bbs_ids = mot_tracker.update(allbbox)   

    for d in track_bbs_ids:
        t_size = cv2.getTextSize('person', cv2.FONT_HERSHEY_PLAIN, 1 , 1)[0]
        color = COLORS[int(d[4])%31]
        cv2.rectangle(image,(int(d[0]), int(d[1])),(int(d[2]),int(d[3])), color, 2)
        cv2.putText(image, (str(int(d[4]))), (int((d[0])), int(d[1])), FONT, 1.5, (255,255,255), 1, cv2.LINE_AA)
    
    return(image)

def process_video(video,ext):
    cap = cv2.VideoCapture('test_videos/'+video+'.'+ext)
    fps = int(cap.get(5))
    frame_count = int(cap.get(7))
    print("Total time: ",time.strftime("%H:%M:%S", time.gmtime(frame_count/fps)))
    h, w = int(cap.get(3)), int(cap.get(4))
    height = int(h/2 if h>400 else h)
    r = height / h
    width = int(w * r)
    writer = cv2.VideoWriter("output/"+video+'.mp4', cv2.VideoWriter_fourcc(*"mp4v"), fps,(height, width))
    i=1
    start = time.time()
    mot_tracker = Sort()
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret==True:
            frame = cv2.resize(frame, (int(height), int(width)))
            frame = process_image(frame, mot_tracker)
            writer.write(frame)
            
            #FPS and time updater
            fps = i/(time.time()-start)
            remain = time.strftime("%H:%M:%S", time.gmtime((frame_count-i)/fps))
            sys.stdout.write('\rTime Remaining: '+str(remain)+'\tFPS = '+str(fps))
            #print("FPS: %.2f"%fps,"\tTime Remaining: ",remain,end='\r')
            i=i+1
        else:
            break
    cap.release()
    print("\nDone! and saved to {}".format('output/'+video+'.mp4'))
    writer.release()

process_video('max','mp4')

