#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan  6 14:47:30 2020

@author: yalin
"""
import sys 
import cv2
import numpy as np 
import os
import sys
sys.path
sys.path.append('./CycleGAN')
sys.path.append('./Neural_Style')
from imutils import paths
from PIL import Image
#torch&torchvision
import torch
import torchvision.transforms as transforms
from torchvision.utils import save_image
from torch.autograd import Variable

# CycleGAN 
from CycleGAN.models import Generator
from CycleGAN.datasets import ImageDataset

#Qt5
from PyQt5.QtWidgets import (QWidget, QLabel, QPushButton, QApplication, QHBoxLayout, QVBoxLayout)

from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QThread, pyqtSignal, Qt
#Neural_Style
from Neural_Style.transformer_net import TransformerNet 

#%%                        
class GAN():
    def __init__(self,ModelStyle,device,video=False):
        self.ModelStyle = ModelStyle # 0:cycle GAN
        self.model =None    # model loader
        self.Trm = None     # transformer
        self.DEVICE = device
        #self.imgPath = imagePath # the image to be style
        self.video = video
        
        if self.ModelStyle == 0: mode ='cycleGAN'
        elif self.ModelStyle ==1 : mode = 'Neural_Style'
        self.weight_path = './pretrained_model/{}/{}_weight.pkl'.format(mode)
    #%% Initialize the models
    def CycleGAN_init(self):
        model = Generator(input_nc=3, output_nc=3, n_residual_blocks=9)
        model.load_state_dict(torch.load(self.weight_path, map_location = self.DEVICE))
        model.to(self.DEVICE)
        model.eval()
        self.model = model
        trm = transforms.Compose([
        transforms.ToTensor(),
        #transforms.Lambda(lambda x: x*255)  Neural_Style
        transforms.Normalize((0.5,0.5,0.5), (0.5,0.5,0.5))  # cycleGAN
        ])
        self.Trm = trm
    def NeuralStyle_init(self):
        model = TransformerNet()
        model.load_state_dict(torch.load(self.weight_path,map_location = self.DEVICE))
        model.cuda()
        model.eval()
        self.Model = model
    
        trm = transforms.Compose([
            transforms.ToTensor(),
            transforms.Lambda(lambda x: x*255)
        ])
        self.Trm = trm
    #%% define a function to convert image from opencv to qtformat
    def cv2QtFormat(self,cv_image):
        rgbImage = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
        convertToQtFormat = QImage(rgbImage.data, rgbImage.shape[1], rgbImage.shape[0], QImage.Format_RGB888)
        convertToQtFormat = QPixmap.fromImage(convertToQtFormat)
        p = convertToQtFormat.scaled(256, 256)
        return p
    # define transfer function
    def Transfer(self,img):
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        # img is RGB for model processing
        img = Image.fromarray(img).resize((256,256))
    
        img = self.Trm(img).to(self.DEVICE)
        # img is RGB,perform style transfer
        t_img = self.Model(img.unsqueeze(0)).data.squeeze(0).cpu()
        
        if self.ModelStyle==1: # Neural_style 
            t_img /=255  
        if self.ModelStyle==0: # cycleGAN
            t_img = 0.5*(t_img + 1.0)
            
        t_img[t_img > 1] = 1
        t_img[t_img < 0] = 0
        img = transforms.ToPILImage()(t_img)
        img = np.array(img)
        
        #img to be dispalyed
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR) 
        return img
    '''
    def VideoRun(self):
        Thread(device = self.DEVICE, model = self.Model, self.transfer,self.cv2QtFormat)
        
        # define a thread
        self.th = Thread(self)
        self.th.changePixmap2.connect(image2.setPixmap)
        self.th.changePixmap3.connect(image3.setPixmap)
        self.th.start()

        self.show()
        return
    def PhotoRun(self):
        return
    
    def run(self):
        if self.video: 
            self.VideoRun()
        else: 
            self.PhotoRun()
    '''
#%%
'''
# define window
class Window(QWidget):
    Dic_God = {'modelIndex': 1, 'weight_path': "Neural_Style/checkpoints/GodBearer.pth",
    'image_path': "Neural_Style/outputs/style.jpg"}
    Dic_Pic = {'modelIndex': 1, 'weight_path': "Neural_Style/checkpoints/picasso.pth",
    'image_path': "Neural_Style/outputs/picasso.jpg"}
    Dic_Van = {'modelIndex': 0, 'weight_path': "CycleGAN/outputs/VanGogh.pth",
    'image_path': "CycleGAN/outputs/VanGogh.jpg"}
    Dic_Mon = {'modelIndex': 0, 'weight_path': "CycleGAN/outputs/monet.pth",
    'image_path': "CycleGAN/outputs/monet.jpg"}


    def __init__(self):
        super().__init__()
        self.Init_UI()
        self.mode

    def Init_UI(self):

        self.setGeometry(300,300,800,500)
        self.setWindowTitle('Style_Transfer')

        # define text 
        text4 = QLabel(self)
        text4.setText("You can click buttons below to change style.")

        # define 4 buttons
        button1 = QPushButton('0Transfer_Godbearer', self)
        button2 = QPushButton('1Transfer_Picasso', self)
        button3 = QPushButton('CycleGAN_VanGogh', self)
        button4 = QPushButton('CycleGAN_Monet', self)

        # adjust locations of buttons
        vbox = QVBoxLayout()
        vbox.addStretch(1)
        vbox.addWidget(text4)
        vbox.addWidget(button1)
        vbox.addWidget(button2)
        vbox.addWidget(button3)
        vbox.addWidget(button4)

        hbox = QHBoxLayout()
        hbox.addStretch(1)
        hbox.addLayout(vbox)

        self.setLayout(hbox)

        # connect buttons with function
        button1.clicked.connect(self.mode = 0)
        button2.clicked.connect(self.mode =1)
        #button3.clicked.connect(lambda: self.Creat_Model(self.Dic_Van))
        #button4.clicked.connect(lambda: self.Creat_Model(self.Dic_Mon))

        # define text to interpret images
        text1 = QLabel(self)
        text2 = QLabel(self)
        text3 = QLabel(self)

        text1.setText('style_image')
        text2.setText('video_image')
        text3.setText('Transfer_image')

        text1.move(115, 260)
        text2.move(385, 260)
        text3.move(655, 260)

        # define 3 images
        self.image1 = QLabel(self) #style image
        image2 = QLabel(self)   #video image
        image3 = QLabel(self)   #transfer image

        self.image1.resize(256, 256)
        image2.resize(256, 256)
        image3.resize(256, 256)

        self.image1.move(1, 3)
        image2.move(270, 3)
        image3.move(530, 3)

        # When first opening it, show 3 default images
        pixmap = QPixmap('Neural_Style/outputs/style.jpg')
        pixmap = pixmap.scaled(256, 256)
        self.image1.setPixmap(pixmap)
        pixmap = QPixmap('Neural_Style/outputs/17.png')
        pixmap = pixmap.scaled(256, 256)
        image2.setPixmap(pixmap)
        pixmap = QPixmap('Neural_Style/outputs/out.png')
        pixmap = pixmap.scaled(256, 256)
        image3.setPixmap(pixmap)

        # define a thread
        self.th = Thread(self)
        self.th.changePixmap2.connect(image2.setPixmap)
        self.th.changePixmap3.connect(image3.setPixmap)
        self.th.start()

        self.show()

    def Creat_Model(self, dic):
        torch.cuda.empty_cache()
        if dic['modelIndex'] == 1:
            CycleGAN_init(dic['weight_path'])
        if dic['modelIndex'] == 2:
            NeuralStyle_init(dic['weight_path'])

        G.ModelIndex = dic['modelIndex']
        pixmap = QPixmap(dic['image_path'])
        pixmap = pixmap.scaled(256, 256)
        self.image1.setPixmap(pixmap)
    '''