from __future__ import print_function
from importlib.metadata import metadata
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow,QFileDialog,QMessageBox,QWidget
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from GUIASS9V3 import Ui_MainWindow
import qdarkstyle
from PyQt5.QtGui import QPixmap
from PIL import Image
from PIL.ExifTags import TAGS
import os.path
import os
#import scipy.misc
import imageio
from pydicom import dcmread
from pydicom.data import get_testdata_file
import numpy
import numpy as np
from PIL.ImageQt import ImageQt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import cv2
import math
from mplwidget import MplWidget 
#from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import random
import matplotlib.image as img
from skimage.data import shepp_logan_phantom
from skimage.transform import radon , rescale , iradon 


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        #Variables
        self.data=[]
        self.greyImageArray=[]
        self.binaryImageArray=[]
        self.kernelArray=[]
        self.kernelArrayFourierFilter=[]
        self.structuralElementArray=[]
        self.padedkernelFourierFilter=[]
        self.kernelSize=1
        self.kernelSizeFourierFilter=1
        self.k_Factor=1
        self.factor=0.1
        self.flag=1
        self.ui.Multiplication_Factor_lineEdit.setText("1")#initialize multiplication factor
        ##add the T image
        image = Image.open("TImage.jpg")#store the data and meta data of the image
        self.original_T_ImageArray=numpy.asarray(image).astype(int)
        #print(self.original_T_ImageArray)
        self.drawimage(0,self.original_T_ImageArray)
        #triggers and connections
        self.ui.actionBrowse_Image.triggered.connect(self.Browsefile) #button to call function browse
        self.ui.actionHistogram_Equalization.triggered.connect(self.Normalize_Equalize_Display_Image) #button to call function browse
        self.ui.actionMedian_Filter_Salt_and_Pepper.triggered.connect(self.saltAndPeperNoise) #button to call function browse
        self.ui.actionSmoothing_Filter.triggered.connect(self.enhancedImageResult)
        self.ui.actionFourier_Domain.triggered.connect(self.fourierdomainfunction)
        self.ui.actionNoise_Filtering.triggered.connect(lambda:self.draw_CreatedImage_noisefiltering())
        self.ui.actionBack_Projection.triggered.connect(self.backProjectionFunction)
        self.ui.actionMorphological_operations.triggered.connect(self.morphologicalFunction)
        self.ui.checkBox_nearest.stateChanged.connect(lambda: self.state_changed(0))
        self.ui.checkBox_linear.stateChanged.connect(lambda: self.state_changed(1))
        self.ui.ChooseROIRegion_NoiseFiltering_pushButton.clicked.connect(lambda: self.ROI_region_select())
        self.ui.lineEdit.returnPressed.connect(self.getfactor)
        self.ui.Angle_lineEdit.returnPressed.connect(self.getAngle)
        self.ui.Kernel_Size_lineEdit.returnPressed.connect(self.arangeKernel)
        self.ui.kernelSize_FourierFiltering_lineEdit.returnPressed.connect(self.arangeKernelFourierFiltering)
        self.ui.StructuralElement_Morphology_LineEdit.returnPressed.connect(self.arangestructruralElementMrophology)
        self.ui.actionPeriodic_Noise_Removal.triggered.connect(self.arangePeriodicNoiseRemoval)
        self.ui.Multiplication_Factor_lineEdit.returnPressed.connect(self.get_K_Factor)
        self.ui.comboBox.currentIndexChanged.connect(self.getAngle)
        self.ui.ChooseNoiseType_NoiseFIltering_comboBox.currentIndexChanged.connect(self.added_noise_noisefiltering)
        self.ui.radioButton_positive.toggled.connect(lambda: self.ShearingHorizontally(0))
        self.ui.radioButton_negative.toggled.connect(lambda: self.ShearingHorizontally(1))     
        self.ui.chooseSEshape_Morphology_ComboBox.currentIndexChanged.connect(self.arangestructruralElementMrophology)




        





    def Browsefile(self):
        self.path = QFileDialog.getOpenFileName(self, 'Open a file', '') #open browse window
        if self.path != ('', ''):
            self.data = self.path[0]
            ###
            #testImage = img.imread(self.path)

            ###  #get the file path only from the openfilename
            if self.data.find(".dcm") !=-1: #test if it is dcm call readdata for dicom
                #self.readdatadicom()
                try: # test if somthing is wrong with the file display the msg if nothing wrong display the image
                    self.readdatadicom()
                except:
                    self.messagebox('Error Occured: this Image is Corrupted, Upload another image')
                    self.resettext()
                    self.greyImageArray=[]
            else:
                #self.readmetadata()#sheel dah law shghalt el try we el except
                try: # test if somthing is wrong with the file display the msg if nothing wrong display the image
                    self.readmetadata()
                except:
                    #self.ui.ImageDisplay_label.setText("This Image is Corrupted, Upload another image")
                    self.messagebox('Error Occured: this Image is Corrupted, Upload another image')
                    self.resettext()
                    self.greyImageArray=[] 
                else:
                    self.displaymetadata() 

    def readmetadata(self):
        self.ui.ImageDisplay_label.setPixmap(QPixmap(self.data))#upload the image using Qpixmap function and set it as label background
        self.ui.ImageDisplay_label.setScaledContents(1)#scale the image to fill the label
        image = Image.open(self.data)#store the data and meta data of the image
        self.imgheight=image.height #get image height
        self.imgwidth=image.width   #get image width
        self.imgmode=image.mode     #get image mode
        self.originalimagearray=numpy.asarray(image).astype(float)
        self.bitsperpixel=round(numpy.log2((numpy.max(self.originalimagearray)-numpy.min(self.originalimagearray)))) #get the bitdepth from the array
        self.filesizeinbit=image.height*image.width*self.bitsperpixel #get the image mode from the image data and find the bitdepth from the all mode array and multiply by width and height 
        #self.ui.Before_graphicsView.canvas.axes.imshow(self.originalimagearray)
        #self.ui.Before_graphicsView.canvas.axes.draw(self)
        
        #self.filesizeinbit=os.path.getsize(self.data)*8
        #file_size = os.stat(str(self.data))
        #print("Size of file :", file_size.st_size*8, "bits")
        #self.bitsperpixel=self.allModes[image.mode] #get the bitdepth from the array
        if (image.mode=="RGB" or image.mode=="L" ):
            self.convert2grey(0)
            self.flag=1 # this flag is used to now if the user added an image or not
            #self.greyImageArray=np.round(self.normalizeUsingEqn(self.greyImageArray,0,1))

            

            #Dilation
            # self.greyImageArray=np.array([[0,0,0,0,0,0,0,0,0,0,0],
            #                               [0,1,1,1,1,0,0,1,1,1,0],
            #                               [0,1,1,1,1,0,0,1,1,1,0],
            #                               [0,1,1,1,1,1,1,1,1,1,0],
            #                               [0,1,1,1,1,1,1,1,1,1,0],
            #                               [0,1,1,0,0,0,1,1,1,1,0],
            #                               [0,1,1,0,0,0,1,1,1,1,0],
            #                               [0,1,1,0,0,0,1,1,1,1,0],
            #                               [0,1,1,1,1,1,1,1,0,0,0],
            #                               [0,1,1,1,1,1,1,1,0,0,0],
            #                               [0,0,0,0,0,0,0,0,0,0,0]])

            #Erosion
            # self.greyImageArray=np.array([[1,1,1,1,1,1,1,1,1,1,1,1,1],
            #                               [1,1,1,1,1,1,0,1,1,1,1,1,1],
            #                               [1,1,1,1,1,1,1,1,1,1,1,1,1],
            #                               [1,1,1,1,1,1,1,1,1,1,1,1,1],
            #                               [1,1,1,1,1,1,1,1,1,1,1,1,1],
            #                               [1,1,1,1,1,1,1,1,1,1,1,1,1],
            #                               [1,1,1,1,1,1,1,1,1,1,1,1,1],
            #                               [1,1,1,1,1,1,1,1,1,1,1,1,1],
            #                               [1,1,1,1,1,1,1,1,1,1,1,1,1],
            #                               [1,1,1,1,1,1,1,1,1,1,1,1,1],
            #                               [1,1,1,1,1,1,1,1,1,1,1,1,1],
            #                               [1,1,1,1,1,1,1,1,1,1,1,1,1],
            #                               [1,1,1,1,1,1,1,1,1,1,1,1,1]])

            #Draw the image directly on the Spatial filter Tab
            self.drawSpatialFilterTab(0,self.greyImageArray)

            #Draw the image directly on the Fourier filter Tab
            self.drawFourierFilterTab(0,self.greyImageArray)
        else:
            self.flag=0

        
        self.binaryImageArray=np.asarray(image.convert('1'))
        #Draw the image directly on the Morphology Tab
        self.drawInMorphologyTab(0,self.binaryImageArray)        
        



 
  

    def displaymetadata(self):
        #display all you read from the image meta data you got from th readmetadata function 
        self.ui.IWdisplay_label.setText(str(self.imgwidth))    
        self.ui.IHdisplay_label.setText(str(self.imgheight))
        self.ui.ICdisplay_label.setText(str(self.imgmode))
        self.ui.ISdisplay_label.setText(str(self.filesizeinbit))
        self.ui.BDdisplay_label.setText(str(self.bitsperpixel))
        self.ui.MUdisplay_label.setText("Not Available")
        self.ui.PNdisplay_label.setText("Not Available")
        self.ui.PAdisplay_label.setText("Not Available")
        self.ui.BPdisplay_label.setText("Not Available")

    def resettext(self):
        # because when changing between corrupted and none corrupted images some meta data could be read but the image itself not so i must reset every thing
        self.ui.IWdisplay_label.setText("Not Available")
        self.ui.IHdisplay_label.setText("Not Available")
        self.ui.BDdisplay_label.setText("Not Available")
        self.ui.ICdisplay_label.setText("Not Available")
        self.ui.ISdisplay_label.setText("Not Available")
        self.ui.MUdisplay_label.setText("Not Available")
        self.ui.PNdisplay_label.setText("Not Available")
        self.ui.PAdisplay_label.setText("Not Available")
        self.ui.BPdisplay_label.setText("Not Available")    

    def readdatadicom(self):
        #self.datafordicom=self.data[self.data.rfind('/')+1:]
        #print(self.datafordicom)
        #fpath = get_testdata_file(str(self.data))
        #print(fpath)

        #new_image=self.ds.pixel_array.astype(float) #convert the array to float to not loose data
        #scaled_image=(np.maximum(new_image,0)/new_image.max())*(2^self.ds.BitsStored) #normalize the array from 0-255 
        #imageio.imwrite('outfile.bmp',new_image) #open a file and write the data you normalized in it

        self.ds = dcmread(self.data) #read all dicom file data
        #print(self.ds)
        imageio.imwrite('outfile.bmp',self.ds.pixel_array.astype(float)) #open a file and write the data you normalized in it
        self.ui.ImageDisplay_label.setPixmap(QPixmap('outfile.bmp'))#upload the image using Qpixmap function and set it as label background
        self.ui.ImageDisplay_label.setScaledContents(1)#scale the image to fill the label
        self.greyImageArray=numpy.asarray(self.ds.pixel_array.astype(float))#read data and put in an array to deal with it easily

        #Draw image directly in the Spatial Filter tab 
        self.drawSpatialFilterTab(0,self.greyImageArray)
        
        #try searching for each attribute if found display it if not display not found
        try:
            self.imgheight=self.ds.Columns
        except:
            self.ui.IHdisplay_label.setText(str("Columns Not Found")) 
        else:
            self.ui.IHdisplay_label.setText(str(self.imgheight))   

        try:
            self.imgwidth=self.ds.Rows
        except:
            self.ui.IWdisplay_label.setText(str("Rows Not Found"))
        else:
            self.ui.IWdisplay_label.setText(str(self.imgwidth))

        try:
            self.imgmode=self.ds.PhotometricInterpretation
        except:
            self.ui.ICdisplay_label.setText(str("Image Mode Not Found"))  
        else:
            self.ui.ICdisplay_label.setText(str(self.imgmode))

        try:
            self.bitsperpixel=self.ds.BitsStored
        except:
            self.ui.BDdisplay_label.setText(str("Bit depth Not Found"))
        else:
            self.ui.BDdisplay_label.setText(str(self.bitsperpixel))
        

        try:
            self.filesizeinbit=self.imgheight*self.imgwidth*self.ds.BitsStored
        except:
            self.ui.ISdisplay_label.setText(str("File Size Not Found"))
        else:
            self.ui.ISdisplay_label.setText(str(self.filesizeinbit))
        
        
        try:
            self.imgModalitity=self.ds.Modality
        except:
            self.ui.MUdisplay_label.setText(str("Modality Not Found"))
        else:
            self.ui.MUdisplay_label.setText(str(self.imgModalitity))        
        
        try:
            self.patientAge=self.ds.PatientAge
        except:
            self.ui.PAdisplay_label.setText(str("Age Not Found")) 
        else:
            self.ui.PAdisplay_label.setText(str(self.patientAge)) 

        try:
            self.patientName=self.ds.PatientName
        except:
            self.ui.PNdisplay_label.setText(str("Patient Name Not Found"))
        else:
            self.ui.PNdisplay_label.setText(str(self.patientName))                   

        #i found out that body part examined could be in bodypartexamined attribute or in study description so i test if found in body part display it if not try study description
        try:
            self.bodypartexamineted=self.ds.BodyPartExamined
        except:
            self.study_description()
        else:
            self.ui.BPdisplay_label.setText(str(self.bodypartexamineted))


    def  study_description(self):
        # to test if the study description found, if found display it if not display Body part Not found 
        try:
            self.bodypartexamineted=self.ds.StudyDescription
        except:
            self.ui.BPdisplay_label.setText(str("Bodypart Examineted Not Found"))
        else:
            self.ui.BPdisplay_label.setText(str(self.bodypartexamineted)) 

        #self.bodypartexamineted=self.ds.StudyDescription
        #self.bodypartexamineted=self.ds.BodyPartExamined

    #def displaymetadatadicom(self):
        #self.ui.IWdisplay_label.setText(str(self.imgwidth))    
        #self.ui.IHdisplay_label.setText(str(self.imgheight))
        #self.ui.ICdisplay_label.setText(str(self.imgmode))
        #self.ui.ISdisplay_label.setText(str(self.filesizeinbit))
        #self.ui.BDdisplay_label.setText(str(self.bitsperpixel))
        #self.ui.MUdisplay_label.setText(str(self.imgModalitity))
        #self.ui.PAdisplay_label.setText(str(self.patientAge))
        #self.ui.PNdisplay_label.setText(str(self.patientName))
        #self.ui.BPdisplay_label.setText(str(self.bodypartexamineted))


    def state_changed(self,x):
        if (x==0):
            if (self.ui.checkBox_nearest.isChecked()):
                self.ui.groupBox_6.hide()
            else:
                self.ui.groupBox_6.show()
        else:
            if (self.ui.checkBox_linear.isChecked()):
                self.ui.groupBox_7.hide()
            else:
                self.ui.groupBox_7.show() 

    def getfactor(self):
        #this means the image is not RGB
        if (self.flag==0):
            self.messagebox("ERORR: Upload an RGB/greyscale image")
            self.ui.lineEdit.clear()
            return
        #there must be an image to resize the factor on it 
        try:
            assert len(self.greyImageArray)!=0
        except:
            self.messagebox("ERORR: Upload the image first then add the factor")
            self.ui.lineEdit.clear()
        else:
            #factor can't be string such as alphabets and typos such as 0.1.1
            try:
                float(self.ui.lineEdit.text())
            except:
                self.messagebox("ERORR: Enter a float/int +ve number & zeros are not accepted")
                self.ui.lineEdit.clear()
            else:
                #factor can't be negative or zero
                try:
                    assert self.ui.lineEdit.text()>str(0)
                except:
                    self.messagebox("ERORR: Enter a +ve number & zeros are not accepted")
                    self.ui.lineEdit.clear()
                else:        
                    self.factor=float(self.ui.lineEdit.text())
                    self.ui.ImageDisplay_label.setScaledContents(0)#donot scale it to see the effect of zooming factor
                    #self.newdimention=int(self.greyImageArray.shape[0]*self.factor)
                    self.newXdimention=round(self.greyImageArray.shape[0]*self.factor)
                    self.newYdimention=round(self.greyImageArray.shape[1]*self.factor)
                    self.ui.H_display_label.setText(str(self.newXdimention))
                    self.ui.W_display_label.setText(str(self.newYdimention))
                    #self.nearest_interpolation()
                    self.nearest_Interpolation()
                    self.linear_Interpolation()

    def getAngle(self):
        try:
            float(self.ui.Angle_lineEdit.text())
        except:
            self.messagebox("ERORR: Enter a float/int +ve or -ve number ")
            self.ui.Angle_lineEdit.clear()
        else:
            self.Rotate(numpy.radians(float(self.ui.Angle_lineEdit.text())),self.original_T_ImageArray)
            if (float(self.ui.Angle_lineEdit.text())>0):
                newstring=str(self.ui.Angle_lineEdit.text())
                self.ui.NewImageDirection_label_display.setText("Left")
                self.ui.NewImageAngle_label_display.setText(newstring)
            elif(float(self.ui.Angle_lineEdit.text())<0):
                newstring=str(float(self.ui.Angle_lineEdit.text())*-1)
                self.ui.NewImageDirection_label_display.setText("Right")
                self.ui.NewImageAngle_label_display.setText(newstring)



    def convert2grey(self,x):
        if (x==0):
            image = Image.open(self.data)#store the data and meta data of the image
            if (image.mode=="RGB"):
                self.greyImage=image.convert('L')
                self.greyImageArray=numpy.asarray(self.greyImage)
            elif(image.mode=='L'):
                self.greyImageArray=numpy.asarray(image)
            else:
                self.messagebox("Please Add an RGB or grey scale image")    

    def scale(self,image):
        gm = image - image.min()
        gs = 255 * (gm / gm.max())
        return gs

    def roundForInterpolation(self,array):
        #print(len(array),array)
        for i in range(len(array)):
                frac,whole=math.modf(array[i])
                if (frac<=0.5):
                    array[i]=whole
                else:
                    array[i]=math.ceil(array[i])
        return array

    def nearest_Interpolation(self):

        # arr=[[0.5,0.56],[2.5,2.67]]
        # arr2=self.roundForInterpolation(arr)
        # print(arr2)
        

        arrangedXArray=numpy.arange(0,self.newXdimention)#initialize an array from 0-(width size)*factor array representing coordinates
        arrangedYArray=numpy.arange(0,self.newYdimention)#initialize an array from 0-(width size)*factor array representing coordinates

        #newpoints=numpy.around(arrangedArray/self.factor)#match each point in the second img with a point in the first img
        newXpoints=self.roundForInterpolation(arrangedXArray/self.factor)#match each point in the second img with a point in the first img
        newYpoints=self.roundForInterpolation(arrangedYArray/self.factor)#match each point in the second img with a point in the first img 
        self.resizedArray=numpy.zeros((self.newXdimention,self.newYdimention))#initialize an array with zeros array of the new image
        self.resizedArray.fill(-1)#fill this array with a value out of range to make it unique

        #self.distanceBetweenNumbers=numpy.zeros((self.greyImageArray.shape[0]*self.factor,self.greyImageArray.shape[1]*self.factor))#initialize an array with zeros
        #self.distanceBetweenNumbers.fill(100000000)#fill this array with a value out of range to make it unique

        for i in range(self.newXdimention):
            for j in range(self.newYdimention):
                if (0<=newXpoints[i]<self.greyImageArray.shape[0] and 0<=newYpoints[j]<self.greyImageArray.shape[1]):
                    #print(i,j)
                    self.resizedArray[i][j]=self.greyImageArray[int(newXpoints[i])][int(newYpoints[j])]  
                else:
                    pass

        self.negativeOnesIndecies=numpy.argwhere(self.resizedArray==-1)
        self.nonNegativeIndecies=numpy.argwhere(self.resizedArray!=-1)
        self.list=[]
        #print(self.negativeOnesIndecies)

        for i in range(len(self.negativeOnesIndecies)):
            for j in range(self.newXdimention):
            #self.list.append(self.nonNegativeIndecies[numpy.searchsorted(self.nonNegativeIndecies,self.negativeOnesIndecies[i])])

                # assume the image is made of 4 quads top-left is the 1st bottom left is the second 
                # bottom-right is the third and the top-right is the fourth
                # and we move diagonaly to search for a non negative value to fill the space with it
                # i chosed to move diagonaly since it is low probability that image data will be empty in the whole diagonal
                # but it can be easily empty for a vertical or horizontal lines
                # j is only used for an incremental to move up,down,left and right of the image

                if ((self.negativeOnesIndecies[i][0]<int((self.newXdimention-1)/2)) and (self.negativeOnesIndecies[i][1]<int((self.newYdimention-1)/2))):#1st quad
                    if (self.resizedArray[int(self.negativeOnesIndecies[i][0]+j)][int(self.negativeOnesIndecies[i][1]+j)]!=-1):
                        self.resizedArray[self.negativeOnesIndecies[i][0]][self.negativeOnesIndecies[i][1]]=self.resizedArray[int(self.negativeOnesIndecies[i][0]+j)][int(self.negativeOnesIndecies[i][1]+j)]
                        break
                elif ((self.negativeOnesIndecies[i][0]>int((self.newXdimention-1)/2)) and (self.negativeOnesIndecies[i][1]<int((self.newYdimention-1)/2))):#2nd quad
                    if (self.resizedArray[int(self.negativeOnesIndecies[i][0]-j)][int(self.negativeOnesIndecies[i][1]+j)]!=-1):
                        self.resizedArray[self.negativeOnesIndecies[i][0]][self.negativeOnesIndecies[i][1]]=self.resizedArray[int(self.negativeOnesIndecies[i][0]-j)][int(self.negativeOnesIndecies[i][1]+j)]
                        break
                elif ((self.negativeOnesIndecies[i][0]>int((self.newXdimention-1)/2)) and (self.negativeOnesIndecies[i][1]>=int((self.newYdimention-1)/2))):#3rd quad
                    if (self.resizedArray[int(self.negativeOnesIndecies[i][0]-j)][int(self.negativeOnesIndecies[i][1]-j)]!=-1):
                        self.resizedArray[self.negativeOnesIndecies[i][0]][self.negativeOnesIndecies[i][1]]=self.resizedArray[int(self.negativeOnesIndecies[i][0]-j)][int(self.negativeOnesIndecies[i][1]-j)]
                        break
                elif ((self.negativeOnesIndecies[i][0]<=int((self.newXdimention-1)/2)) and (self.negativeOnesIndecies[i][1]>int((self.newYdimention-1)/2))):#4th quad
                    if (self.resizedArray[int(self.negativeOnesIndecies[i][0]+j)][int(self.negativeOnesIndecies[i][1]-j)]!=-1):
                        self.resizedArray[self.negativeOnesIndecies[i][0]][self.negativeOnesIndecies[i][1]]=self.resizedArray[int(self.negativeOnesIndecies[i][0]+j)][int(self.negativeOnesIndecies[i][1]-j)]
                        break      
        self.negativeOnesIndecies=numpy.argwhere(self.resizedArray==-1)
        #print(self.negativeOnesIndecies)

        self.greyImageArrayResized=numpy.asarray(self.resizedArray)

           ##### El Mafrood asheel kol dah lama a3rad ezay a7wel men Pil le Qpuxmap 3ala tool
        imageio.imwrite('erock_gray_resized.jpg',self.greyImageArrayResized.astype(float))
        self.ui.Nearest_ImageDisplay.setPixmap(QPixmap('erock_gray_resized.jpg'))#upload the image using Qpixmap function and set it as label background
                     

    def linear_Interpolation(self):
    	#get dimensions of original image
        originalGreyImageArray = numpy.copy(self.greyImageArray)
        originalGreyImageHeight, originalGreyImageWidth = originalGreyImageArray.shape[:2]
        #create an array of the desired shape. 
        #We will fill-in the values later.
        resizedImageHeight = int(originalGreyImageHeight * self.factor)
        resizedImageWidth = int(originalGreyImageWidth * self.factor)
        resized = numpy.zeros((int(resizedImageHeight), int(resizedImageWidth)))
        #Calculate horizontal and vertical scaling factor
        #to get the value of the new image from the old image
        reseprocalfactor=1/self.factor 
        
        for i in range(resizedImageHeight):
            for j in range(resizedImageWidth):
                #map the coordinates back to the original image
                x = i * reseprocalfactor
                y = j * reseprocalfactor
                #calculate the coordinate values for 4 surrounding pixels.
                x_floor = math.floor(x)
                x_ceil = min( originalGreyImageHeight - 1, math.ceil(x))
                y_floor = math.floor(y)
                y_ceil = min(originalGreyImageWidth - 1, math.ceil(y))

                if (x_ceil == x_floor) and (y_ceil == y_floor):
                    newpointvalue = originalGreyImageArray[int(x), int(y)]
                elif (x_ceil == x_floor):
                    star1 = originalGreyImageArray[int(x), int(y_floor)]
                    star2 = originalGreyImageArray[int(x), int(y_ceil)]
                    newpointvalue = star1 * (y_ceil - y) + star2 * (y - y_floor)
                elif (y_ceil == y_floor):
                    star1 = originalGreyImageArray[int(x_floor), int(y)]
                    star2 = originalGreyImageArray[int(x_ceil), int(y)]
                    newpointvalue = (star1 * (x_ceil - x)) + (star2	 * (x - x_floor))
                else:
                    vertix1 = originalGreyImageArray[x_floor, y_floor]
                    vertix2 = originalGreyImageArray[x_ceil, y_floor]
                    vertix3 = originalGreyImageArray[x_floor, y_ceil]
                    vertix4 = originalGreyImageArray[x_ceil, y_ceil]

                    star1 = vertix1 * (x_ceil - x) + vertix2 * (x - x_floor)
                    star2 = vertix3 * (x_ceil - x) + vertix4 * (x - x_floor)
                    newpointvalue = star1 * (y_ceil - y) + star2 * (y - y_floor)

                resized[i,j] = newpointvalue
        imageio.imwrite('erock_gray_resized_Interpolate.jpg',resized.astype(float))
        self.ui.Linear_ImageDisplay.setPixmap(QPixmap('erock_gray_resized_Interpolate.jpg'))#upload the image using Qpixmap function and set it as label background
           
    def Rotate(self,angle,array):
        rotated = numpy.zeros((array.shape[0], array.shape[1]))
        centerX,centerY=int(array.shape[0]/2),int(array.shape[1]/2)
        for i in range(array.shape[0]):
            for j in range(array.shape[1]):
                newX=(i-centerX)*numpy.cos(angle)+(j-centerY)*numpy.sin(angle)+centerX
                newY=-(i-centerX)*numpy.sin(angle)+(j-centerY)*numpy.cos(angle)+centerY

                # if nearest do this
                if (self.ui.comboBox.currentIndex()==0):
                    #just Round using the nearest interpolation rounding method and thats it the nearest interpolation is done  
                    newX=self.roundforRotation(newX)
                    newY=self.roundforRotation(newY)
                    if (newX>=0 and newY>=0 and newX<array.shape[0] and  newY<array.shape[1]):
                        rotated[i,j]=array[int(newX),int(newY)] 
                else:
                    # if linear do this

                    # here we are trying to get the pixles before and after the pixle we got which is probably is a non integer number
                    x_floor = math.floor(newX)
                    x_ceil = min(array.shape[0] - 1, math.ceil(newX))
                    y_floor = math.floor(newY)
                    y_ceil = min(array.shape[1] - 1, math.ceil(newY))

                    # first thing is to check if it is between the boundaries or not
                    if (newX>=0 and newY>=0 and newX<array.shape[0] and  newY<array.shape[1]):
                        if (x_ceil == x_floor) and (y_ceil == y_floor):
                            # if it is int number get it from the array directly
                            newpointvalue = array[int(newX), int(newY)]
                        elif (x_ceil == x_floor):
                            # if the image has the same X so it is on the same horixontal axis so get the star from the vertical axis 
                            star1 = array[int(newX), int(y_floor)]
                            star2 = array[int(newX), int(y_ceil)]
                            newpointvalue = star1 * (y_ceil - newY) + star2 * (newY - y_floor)
                        elif (y_ceil == y_floor):
                            # if the image has the same Y so it is on the same Vertical axis so get the star from the horizontal axis 
                            star1 = array[int(x_floor), int(newY)]
                            star2 = array[int(x_ceil), int(newY)]
                            newpointvalue = (star1 * (x_ceil - newX)) + (star2	 * (newX - x_floor))
                        else:
                            #get all possible verticies and get from them the stars then use the stars to get the new point
                            vertix1 = array[x_floor, y_floor]
                            vertix2 = array[x_ceil, y_floor]
                            vertix3 = array[x_floor, y_ceil]
                            vertix4 = array[x_ceil, y_ceil]

                            star1 = vertix1 * (x_ceil - newX) + vertix2 * (newX - x_floor)
                            star2 = vertix3 * (x_ceil - newX) + vertix4 * (newX - x_floor)
                            newpointvalue = star1 * (y_ceil - newY) + star2 * (newY - y_floor)
                        # assign the new point you calculated to the array
                        rotated[i,j] = newpointvalue
                    
        self.drawimage(1,rotated.astype(int))
       

    def ShearingHorizontally(self,s):
        # if the user choosed the 45 deg
        if (s==0):
            # since the angles are even -45 or 45 so this means the seharing hosizontally factor is equal 0.414 and -0.414 respectivley
            shear=-0.414
            # the new dimension will be the original array dimesion* shearing factor then fill it with zeros     
            newXdimension=round(self.original_T_ImageArray.shape[1])
            sheared = numpy.zeros((self.original_T_ImageArray.shape[0], newXdimension))
            for i in range(self.original_T_ImageArray.shape[0]):
                for j in range(self.original_T_ImageArray.shape[1]):

                    # if it is +45 this means shearing factor equal to 1 so i used the rule, but with a slight differnce that the vertical axis 
                    # in the rule was increasing upwards and here in the image vertical is increasing downwards so i made it to increase upwards
                    newX=j + shear*(i)+20
                    newX=round(newX)
                    if (0<=newX<newXdimension):
                        sheared[i][newX]=self.original_T_ImageArray[i][j]
            self.ui.NewImageDirection_label_display.setText("Right")
            self.ui.NewImageAngle_label_display.setText("45")            
        else:
            # since the angles are even -45 or 45 so this means the seharing hosizontally factor is equal 0.414 and -0.414 respectivley
            shear = 0.414
            # the new dimension will be the original array dimesion* shearing factor then fill it with zeros  
            newXdimension=round(self.original_T_ImageArray.shape[0],self.original_T_ImageArray.shape[1])
            sheared = numpy.zeros((self.original_T_ImageArray.shape[0], newXdimension))
            for i in range(self.original_T_ImageArray.shape[0]):
                for j in range(self.original_T_ImageArray.shape[1]):

                    # if it is -45 this means shearing factor equal to -1 so I used the rule, but with a slight differnce that the vertical axis 
                    # in the rule was increasing upwards and here in the image vertical is increasing downwards, so that mean the space that was supposed 
                    # supposed to be left from the leftside if the image vertical axis increases upward will be the same as the rightside of the image vertical axis increadsing doenward
                    newX=j + shear*(i)-20
                    newX=round(newX)
                    if (0<=newX<newXdimension):
                        sheared[i][newX]=self.original_T_ImageArray[i][j]  
            self.ui.NewImageDirection_label_display.setText("Left")
            self.ui.NewImageAngle_label_display.setText("-45")                                        

        self.drawimage(1,sheared.astype(int))

    
    def drawimage(self,x,array):
        if (x==1): 
            self.ui.after.canvas.axes.clear()
            self.ui.after.canvas.axes.imshow(array,cmap="gray")#int is nesceray
            self.ui.after.canvas.draw()
        elif(x==0):
            self.ui.before.canvas.axes.clear()
            self.ui.before.canvas.axes.imshow(array,cmap="gray")#int is nesceray
            self.ui.before.canvas.draw()
        elif(x==2):
            self.ui.Original_Image_display.canvas.axes.clear()
            self.ui.Original_Image_display.canvas.axes.imshow(array,cmap="gray")    
            self.ui.Original_Image_display.canvas.draw()
        elif(x==3):
            self.ui.Equalized_Image_display.canvas.axes.clear()
            self.ui.Equalized_Image_display.canvas.axes.imshow(array,cmap="gray")    
            self.ui.Equalized_Image_display.canvas.draw()

    def drawhistogram(self,v,x,y):
        if (v==0):
            self.ui.Original_Histogram_display.canvas.axes.clear()
            self.ui.Original_Histogram_display.canvas.axes.bar(x,y)  
            self.ui.Original_Histogram_display.canvas.draw()  
        elif(v==1):
            self.ui.Equalized_Histogram_display.canvas.axes.clear()
            self.ui.Equalized_Histogram_display.canvas.axes.bar(x,y)   
            self.ui.Equalized_Histogram_display.canvas.draw()

    def drawSpatialFilterTab(self,i,array):
        if (i==0):
            self.ui.Original_Image_SpatialFilter_display.canvas.axes.clear()
            self.ui.Original_Image_SpatialFilter_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.Original_Image_SpatialFilter_display.canvas.draw()
        elif(i==1):
            self.ui.Enhanced_Original_Image_SpatialFilter_display.canvas.axes.clear()
            self.ui.Enhanced_Original_Image_SpatialFilter_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.Enhanced_Original_Image_SpatialFilter_display.canvas.draw()
        elif(i==2):
            self.ui.Noisy_Image_SpatialFilter_display.canvas.axes.clear()
            self.ui.Noisy_Image_SpatialFilter_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.Noisy_Image_SpatialFilter_display.canvas.draw()
        elif(i==3):
            self.ui.NonNoisy_Image_SpatialFilter_display.canvas.axes.clear()
            self.ui.NonNoisy_Image_SpatialFilter_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.NonNoisy_Image_SpatialFilter_display.canvas.draw()


    def drawFourierFilterTab(self,i,array):
        if (i==0):
            self.ui.Original_Image_FourierFiltering_display.canvas.axes.clear()
            self.ui.Original_Image_FourierFiltering_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.Original_Image_FourierFiltering_display.canvas.draw()
        elif(i==1):
            self.ui.Filtered_Image_FourierFiltering_display.canvas.axes.clear()
            self.ui.Filtered_Image_FourierFiltering_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.Filtered_Image_FourierFiltering_display.canvas.draw()
        elif(i==2):
            self.ui.Diff_fromspatiaandfourier_FourierFiltering_display.canvas.axes.clear()
            self.ui.Diff_fromspatiaandfourier_FourierFiltering_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.Diff_fromspatiaandfourier_FourierFiltering_display.canvas.draw()
        elif(i==3):
            self.ui.PeriodicNoiseRemoval_FourierFiltering_display.canvas.axes.clear()
            self.ui.PeriodicNoiseRemoval_FourierFiltering_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.PeriodicNoiseRemoval_FourierFiltering_display.canvas.draw()            

    def drawInFourierdomainTab(self,i,array):
        if (i==0):
            self.ui.Original_image_fourierdomain_display.canvas.axes.clear()
            self.ui.Original_image_fourierdomain_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.Original_image_fourierdomain_display.canvas.draw()
        elif(i==1):
            self.ui.magnitudebeforelog_image_fourierdomain_display.canvas.axes.clear()
            self.ui.magnitudebeforelog_image_fourierdomain_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.magnitudebeforelog_image_fourierdomain_display.canvas.draw()
        elif(i==2):
            self.ui.phasebeforelog_image_fourierdomain_display.canvas.axes.clear()
            self.ui.phasebeforelog_image_fourierdomain_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.phasebeforelog_image_fourierdomain_display.canvas.draw()
        elif(i==3):
            self.ui.magnitudeafterlog_image_fourierdomain_display.canvas.axes.clear()
            self.ui.magnitudeafterlog_image_fourierdomain_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.magnitudeafterlog_image_fourierdomain_display.canvas.draw()
        elif(i==4):
            self.ui.phaseafterlog_image_fourierdomain_display.canvas.axes.clear()
            self.ui.phaseafterlog_image_fourierdomain_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.phaseafterlog_image_fourierdomain_display.canvas.draw()                  

    def drawInBackProjectionTab(self,i,array):
        if (i==0):
            self.ui.phantomImage_BackProjection_display.canvas.axes.clear()
            self.ui.phantomImage_BackProjection_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.phantomImage_BackProjection_display.canvas.draw()
        elif(i==1):
            self.ui.phantomSinogram_BackProjection_display.canvas.axes.clear()
            self.ui.phantomSinogram_BackProjection_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.phantomSinogram_BackProjection_display.canvas.draw()
        elif(i==2):
            self.ui.phantomlaminogram_NoFilter_specificAngles_BackProjection_display.canvas.axes.clear()
            self.ui.phantomlaminogram_NoFilter_specificAngles_BackProjection_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.phantomlaminogram_NoFilter_specificAngles_BackProjection_display.canvas.draw()
        elif(i==3):
            self.ui.phantomlaminogram_NoFilter_allAngles_BackProjection_display.canvas.axes.clear()
            self.ui.phantomlaminogram_NoFilter_allAngles_BackProjection_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.phantomlaminogram_NoFilter_allAngles_BackProjection_display.canvas.draw()
        elif(i==4):
            self.ui.phantomlaminogram_RamlakFilter_allAngles_BackProjection_display.canvas.axes.clear()
            self.ui.phantomlaminogram_RamlakFilter_allAngles_BackProjection_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.phantomlaminogram_RamlakFilter_allAngles_BackProjection_display.canvas.draw()
        elif(i==5):
            self.ui.phantomlaminogram_HammingFilter_allAngles_BackProjection_display.canvas.axes.clear()
            self.ui.phantomlaminogram_HammingFilter_allAngles_BackProjection_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.phantomlaminogram_HammingFilter_allAngles_BackProjection_display.canvas.draw()           

    def drawInMorphologyTab(self,i,array):
        if (i==0):
            self.ui.ImageBefore_Morphologhy_display.canvas.axes.clear()
            self.ui.ImageBefore_Morphologhy_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.ImageBefore_Morphologhy_display.canvas.draw()
            print("Before: ",array)
        elif(i==1):
            self.ui.ImageAfter_Morphologhy_display.canvas.axes.clear()
            self.ui.ImageAfter_Morphologhy_display.canvas.axes.imshow(array,cmap="gray")
            self.ui.ImageAfter_Morphologhy_display.canvas.draw()
            print("After: ",array)

    def Normalize_Equalize_Display_Image(self):
        if (len(self.greyImageArray)):
            pass
        else:
            self.messagebox("Upload the image first")
            return

        greyimage= (numpy.maximum(self.greyImageArray, 0) / self.greyImageArray.max()) * 255.0
        greyimage=numpy.uint8(greyimage)    

        # empty list to store the count of each intensity value
        frequencey =[]
        equalizedfrequency=[]
        cdf=[]
        sk=[]
        
        # empty list to store intensity value
        Intensity = []
        equalizedImagearray=numpy.zeros((greyimage.shape[0],greyimage.shape[1]))
        equalizedImagearray.fill(50)
        
        imagesize=(greyimage.shape[0]*greyimage.shape[1])

        
        for k in range(0, 256):
            #add all gray intensities which are from 0-255 in an array
            Intensity.append(k)

            #Count the frequency of each intensity in the array
            count=0
            for i in range(greyimage.shape[0]):
                for j in range(greyimage.shape[1]):
                    if (k==greyimage[i][j]):
                        count = count +1

            #Append the intensity frequency in array of frequencies
            frequencey.append(count)


        #To get the probability of the freq of each intensity we must devide all the intensities by imagesize which is imageHeight*imageWidth
        probabilityOfIntensity = [x / imagesize for x in frequencey]
        probabilityOfIntensity=numpy.array(probabilityOfIntensity)#convert it to numpy array to use sum


 
        #get the CDF and the SK of the Intensity frequencies
        for i in range(len(probabilityOfIntensity)):
            cdf.append(numpy.sum(probabilityOfIntensity[:i]))
            sk.append(int(round(numpy.sum(probabilityOfIntensity[:i])*255,0)))
  

        for i in range(len(Intensity)):
            for j in range(greyimage.shape[0]):
                for k in range(greyimage.shape[1]):
                    if (Intensity[i]==greyimage[j][k]):
                        equalizedImagearray[j][k]=sk[i]   
                       

        for k in range(0, 256):

            #Count the frequency of each intensity in the array
            count=0
            for i in range(equalizedImagearray.shape[0]):
                for j in range(equalizedImagearray.shape[1]):
                    if (k==equalizedImagearray[i][j]):
                        count = count +1

            #Append the intensity frequency in array of frequencies
            equalizedfrequency.append(count)            

                
        #To get the probability of the freq of each intensity we must devide all the intensities by imagesize which is imageHeight*imageWidth
        probabilityOfEqualized = [x / imagesize for x in equalizedfrequency]
        probabilityOfEqualized=numpy.array(probabilityOfEqualized)

        self.drawimage(2,greyimage)
        #Plot the frequency on the Y-axis and Intensity on X-axis
        self.drawhistogram(0,Intensity,probabilityOfIntensity)

        self.drawimage(3,equalizedImagearray) 
        #Plot the frequency on the Y-axis and Intensity on X-axis
        self.drawhistogram(1,Intensity,probabilityOfEqualized)

    def arangeKernel(self):  
        #this means the image is not RGB
        if (self.flag==0):
            self.messagebox("ERORR: Upload an RGB/greyscale image")
            self.ui.Kernel_Size_lineEdit.clear()
            return
        #there must be an image to multiply factor on it 
        try:
            assert len(self.greyImageArray)!=0
        except:
            self.messagebox("ERORR: Upload the image first then add the factor")
            self.ui.Kernel_Size_lineEdit.clear()
        else:
            #kernel size can't be string such as alphabets and typos such as 0.1.1
            try:
                int(self.ui.Kernel_Size_lineEdit.text())
            except:
                self.messagebox("ERORR: Enter kernel size as int +ve number & zeros are not accepted")
                self.ui.Kernel_Size_lineEdit.clear()
            else:
                #kernel size can't be negative or zero
                try:
                    assert self.ui.Kernel_Size_lineEdit.text()>str(0) and (int(self.ui.Kernel_Size_lineEdit.text())%2==1)
                except:
                    self.messagebox("ERORR: Enter kernel size as +ve ODD numbers & zeros are not accepted")
                    self.ui.Kernel_Size_lineEdit.clear()
                else:        
                    self.kernelSize=int(self.ui.Kernel_Size_lineEdit.text())
                    self.kernelArray=numpy.ones((self.kernelSize,self.kernelSize))

    def arangePeriodicNoiseRemoval(self):
        try:
            assert len(self.greyImageArray)!=0
        except:
            self.messagebox("ERORR: Upload the image first then add the kernel size")
            self.ui.kernelSize_FourierFiltering_lineEdit.clear()
        else:
            f = numpy.fft.fft2(self.greyImageArray) # changing the image to the frequency domain by fourier 
            fshift = numpy.fft.fftshift(f)

            img_shape = self.greyImageArray.shape

            H1 = self.notch_reject_filter(img_shape, 4, 38, 30)
            H2 = self.notch_reject_filter(img_shape, 4, -42, 27)
            H3 = self.notch_reject_filter(img_shape, 2, 80, 30)
            H4 = self.notch_reject_filter(img_shape, 2, -82, 28)

            NotchFilter = H1*H2*H3*H4
            NotchRejectCenter = fshift * NotchFilter 
            NotchReject = numpy.fft.ifftshift(NotchRejectCenter)
            inverse_NotchReject = numpy.fft.ifft2(NotchReject)  # Compute the inverse DFT of the result

            Result = numpy.abs(inverse_NotchReject)
            self.drawFourierFilterTab(3,Result)


    def notch_reject_filter(self,shape, d0=9, u_k=0, v_k=0):
        P, Q = shape
        # Initialize filter with zeros
        H = numpy.zeros((P, Q))

        # Traverse through filter
        for u in range(0, P): 
            for v in range(0, Q):
                # Get euclidean distance from point D(u,v) to the center
                D_uv = numpy.sqrt((u - P / 2 + u_k) ** 2 + (v - Q / 2 + v_k) ** 2)
                D_muv = numpy.sqrt((u - P / 2 - u_k) ** 2 + (v - Q / 2 - v_k) ** 2)              

                if D_uv <= d0 or D_muv <= d0:
                    H[u, v] = 0.0
                else:
                    H[u, v] = 1.0

        return H

    def arangeKernelFourierFiltering(self):  
        #this means the image is not RGB
        if (self.flag==0):
            self.messagebox("ERORR: Upload an RGB/greyscale image")
            self.ui.kernelSize_FourierFiltering_lineEdit.clear()
            return
        #there must be an image to multiply factor on it 
        try:
            assert len(self.greyImageArray)!=0
        except:
            self.messagebox("ERORR: Upload the image first then add the kernel size")
            self.ui.kernelSize_FourierFiltering_lineEdit.clear()
        else:
            #kernel size can't be string such as alphabets and typos such as 0.1.1
            try:
                int(self.ui.kernelSize_FourierFiltering_lineEdit.text())
            except:
                self.messagebox("ERORR: Enter kernel size as int +ve number & zeros are not accepted")
                self.ui.kernelSize_FourierFiltering_lineEdit.clear()
            else:
                #kernel size can't be negative or zero
                try:
                    assert self.ui.kernelSize_FourierFiltering_lineEdit.text()>str(0) and (int(self.ui.kernelSize_FourierFiltering_lineEdit.text())%2==1)
                except:
                    self.messagebox("ERORR: Enter kernel size as +ve ODD numbers & zeros are not accepted")
                    self.ui.kernelSize_FourierFiltering_lineEdit.clear()
                else:        
                    self.kernelSizeFourierFilter=int(self.ui.kernelSize_FourierFiltering_lineEdit.text())
                    self.kernelArrayFourierFilter=numpy.ones((self.kernelSizeFourierFilter,self.kernelSizeFourierFilter))
                    self.kernelArrayFourierFilter=self.kernelArrayFourierFilter*(1/numpy.sum(self.kernelArrayFourierFilter))
                    if (self.kernelArrayFourierFilter.shape[0]>self.greyImageArray.shape[0] or self.kernelArrayFourierFilter.shape[1]>self.greyImageArray.shape[1]):
                        self.messagebox("Please upload another larger image or reduce kernel size")
                    else:    
                        self.padedkernelFourierFilter=numpy.zeros((int(self.greyImageArray.shape[0]),int(self.greyImageArray.shape[1])))
                        i_start=(int(self.greyImageArray.shape[0])//2)-(self.kernelSizeFourierFilter//2)
                        j_start=(int(self.greyImageArray.shape[1])//2)-(self.kernelSizeFourierFilter//2)
                        self.padedkernelFourierFilter[i_start:i_start+self.kernelSizeFourierFilter,j_start:j_start+self.kernelSizeFourierFilter]+=self.kernelArrayFourierFilter
                        print(self.padedkernelFourierFilter.shape,numpy.sum(self.padedkernelFourierFilter))   
                        greyImageArrayInFrequencyDomain = numpy.fft.fft2(self.greyImageArray)
                        kernelPaddedFourier = numpy.fft.fft2(self.padedkernelFourierFilter)
                        imageLowPassFilter= kernelPaddedFourier* greyImageArrayInFrequencyDomain
                        imageFilteredInFrequencyDomain=numpy.fft.ifft2(imageLowPassFilter)
                        imageFilteredInFrequencyDomain=numpy.fft.fftshift(imageFilteredInFrequencyDomain)
                        imageFilteredInFrequencyDomain=numpy.abs(imageFilteredInFrequencyDomain)
                        self.drawFourierFilterTab(1,imageFilteredInFrequencyDomain)
                        ########################################################################################
                        self.kernelArray=numpy.ones((self.kernelSizeFourierFilter,self.kernelSizeFourierFilter))
                        padwidth=int((self.kernelSizeFourierFilter-1)/2)
                        #padedmatrix=numpy.pad(self.greyImageArray,pad_width=padwidth,mode="constant",constant_values=0)
                        matrix=self.greyImageArray
                        padedimage=numpy.zeros((int(self.greyImageArray.shape[0])+padwidth*2,int(self.greyImageArray.shape[1])+padwidth*2))
                        padedimage[padwidth:int(self.greyImageArray.shape[0])+padwidth,padwidth:int(self.greyImageArray.shape[1]+padwidth)]+=matrix
                        print(self.greyImageArray.shape,padedimage.shape)

                        #initializing variables 
                        convolvedImage=[]
                        subtractedImage=[]
                        kernelSum=numpy.sum(self.kernelArray)#will devide by this number in convolution

                        for i in range(self.greyImageArray.shape[0]):
                            endpointVerical=i+self.kernelSizeFourierFilter
                            rowArray=[]
                            for j in range(self.greyImageArray.shape[1]):
                                endPointHorizontal=j+self.kernelSizeFourierFilter

                                #This row will take each 3x3 array from the padedimage and multiply image by kernel element byb element and then sum all the elements after multipling
                                rowArray.append(numpy.sum(numpy.multiply(padedimage[i:endpointVerical,j:endPointHorizontal],self.kernelArray))/kernelSum)
                            convolvedImage.append(rowArray)
                        convolvedImage=numpy.array(convolvedImage)
                        subtractedDifferenceImage=imageFilteredInFrequencyDomain-convolvedImage
                        subtractedDifferenceImage=self.arrayNormalization(subtractedDifferenceImage)
                        self.drawFourierFilterTab(2,subtractedDifferenceImage)
                
    def arangestructruralElementMrophology(self):
        #this means the image is not RGB
        if (self.flag==0):
            self.messagebox("ERORR: Upload an RGB/greyscale image")
            self.ui.StructuralElement_Morphology_LineEdit.clear()
            return
        #there must be an image to multiply factor on it 
        try:
            assert len(self.binaryImageArray)!=0
        except:
            self.messagebox("ERORR: Upload the image first then add the kernel size")
            self.ui.StructuralElement_Morphology_LineEdit.clear()
        else:
            #kernel size can't be string such as alphabets and typos such as 0.1.1
            try:
                int(self.ui.StructuralElement_Morphology_LineEdit.text())
            except:
                self.messagebox("ERORR: Enter kernel size as int +ve number & zeros are not accepted")
                self.ui.StructuralElement_Morphology_LineEdit.clear()
            else:
                #kernel size can't be negative or zero
                try:
                    assert self.ui.StructuralElement_Morphology_LineEdit.text()>str(1) and (int(self.ui.StructuralElement_Morphology_LineEdit.text())%2==1)
                except:
                    self.messagebox("ERORR: Enter kernel size as +ve ODD numbers & zeros and ones are not accepted")
                    self.ui.StructuralElement_Morphology_LineEdit.clear()
                else:
                    self.structuralElementArray=np.ones((int(self.ui.StructuralElement_Morphology_LineEdit.text()),int(self.ui.StructuralElement_Morphology_LineEdit.text())))
                    if (self.ui.chooseSEshape_Morphology_ComboBox.currentIndex()==0):
                        print("Cross") 
                        self.structuralElementArray[0][0]=0
                        self.structuralElementArray[0][-1]=0
                        self.structuralElementArray[-1][0]=0
                        self.structuralElementArray[-1][-1]=0
                    else:
                        print("Square")    

      

    def get_K_Factor(self):
        #this means the image is not RGB
        if (self.flag==0):
            self.messagebox("ERORR: Upload an RGB/greyscale image")
            self.ui.Multiplication_Factor_lineEdit.clear()
            return
        #there must be an image to multiply factor on it 
        try:
            assert len(self.greyImageArray)!=0
        except:
            self.messagebox("ERORR: Upload the image first then add the factor")
            self.ui.Multiplication_Factor_lineEdit.clear()
        else:
            #factor can't be string such as alphabets and typos such as 0.1.1
            try:
                float(self.ui.Multiplication_Factor_lineEdit.text())
            except:
                self.messagebox("ERORR: Enter multiplication factor as float/int +ve number & zeros are not accepted")
                self.ui.Multiplication_Factor_lineEdit.clear()
            else:
                #factor can't be negative or zero
                try:
                    assert self.ui.Multiplication_Factor_lineEdit.text()>str(0)
                except:
                    self.messagebox("ERORR: Enter multiplication factor as +ve ODD numbers & zeros are not accepted")
                    self.ui.Multiplication_Factor_lineEdit.clear()
                else:        
                    self.k_Factor=float(self.ui.Multiplication_Factor_lineEdit.text())

    def enhancedImageResult(self):
        try:
            assert self.ui.Kernel_Size_lineEdit.text() and self.ui.Multiplication_Factor_lineEdit.text()
        except:
            self.messagebox("Add the Image then, Enter the values of the kernel size and multiplication factor")    
        else:
            #pad width is the added zeros in each side of the image, then pad the image by 0 with the pad width calculated    
            padwidth=int((self.kernelSize-1)/2)
            #padedmatrix=numpy.pad(self.greyImageArray,pad_width=padwidth,mode="constant",constant_values=0)
            matrix=self.greyImageArray
            padedimage=numpy.zeros((int(self.greyImageArray.shape[0])+padwidth*2,int(self.greyImageArray.shape[1])+padwidth*2))
            padedimage[padwidth:int(self.greyImageArray.shape[0])+padwidth,padwidth:int(self.greyImageArray.shape[1]+padwidth)]+=matrix
            print(self.greyImageArray.shape,padedimage.shape)

            #initializing variables 
            convolvedImage=[]
            subtractedImage=[]
            kernelSum=numpy.sum(self.kernelArray)#will devide by this number in convolution

            for i in range(self.greyImageArray.shape[0]):
                endpointVerical=i+self.kernelSize
                rowArray=[]
                for j in range(self.greyImageArray.shape[1]):
                    endPointHorizontal=j+self.kernelSize

                    #This row will take each 3x3 array from the padedimage and multiply image by kernel element byb element and then sum all the elements after multipling
                    rowArray.append(numpy.sum(numpy.multiply(padedimage[i:endpointVerical,j:endPointHorizontal],self.kernelArray))/kernelSum)
                convolvedImage.append(rowArray)
            convolvedImage=numpy.array(convolvedImage)
  
            #subtracted image 
            subtractedImage=self.greyImageArray-convolvedImage

            #multiply by the factor
            enhancedImage=self.k_Factor*subtractedImage + self.greyImageArray

            # normalize the array from 0-255 then darw the normalized array
            #normalizedEnhancedImage=(255*(enhancedImage - numpy.min(enhancedImage))/numpy.ptp(enhancedImage)) #image is slightly darken
            normalizedEnhancedImage=self.arrayNormalization(enhancedImage) #image is slighltly lighter and better
            self.drawSpatialFilterTab(1,normalizedEnhancedImage)
        
    def saltAndPeperNoise(self):

        #check if the grey image is loaded or not if yes continue
        try:
            assert len(self.greyImageArray)!=0
        except:
            self.messagebox("ERORR: Upload the image first then add the factor")
        else:
            noisyImage=numpy.array(self.greyImageArray)#convert the array to numpy array to be assignable
            maxRandomeValue=int(self.greyImageArray.shape[0]*self.greyImageArray.shape[1]/20)# number 20 doesnot refer to any thing but to decrese no. of pixles only
            
            # this will yield 2 random numbers in range between 0 and maxrandomvalue for salt and pepper noise pixles positions
            numberSaltPixles=numpy.random.randint(0,maxRandomeValue)
            numberPeperPixles=numpy.random.randint(0,maxRandomeValue)
            for i in range(numberSaltPixles):
                #get random Coordinates and assign salt (white) 255 value to it
                Xvalue=numpy.random.randint(0,self.greyImageArray.shape[0])
                Yvalue=numpy.random.randint(0,self.greyImageArray.shape[1])
                noisyImage[Xvalue][Yvalue]=255
            for i in range(numberPeperPixles):
                #get random Coordinates and assign pepper (black) 0 value to it
                Xvalue=numpy.random.randint(0,self.greyImageArray.shape[0])
                Yvalue=numpy.random.randint(0,self.greyImageArray.shape[1])
                noisyImage[Xvalue][Yvalue]=0

            #draw the  noisy image    
            self.drawSpatialFilterTab(2,noisyImage)    

            #make a 3x3 median filter and pad the noisy image with 0 value for the pad width calculated
            medianKernelSize=3
            padwidth=int((medianKernelSize-1)/2)
            #padedNoisyImage=numpy.pad(noisyImage,pad_width=padwidth,mode="constant",constant_values=0)
            matrix=self.greyImageArray
            padedNoisyImage=numpy.zeros((int(noisyImage.shape[0])+padwidth*2,int(noisyImage.shape[1])+padwidth*2))
            padedNoisyImage[padwidth:int(noisyImage.shape[0])+padwidth,padwidth:int(noisyImage.shape[1]+padwidth)]+=matrix


            #initialize array
            filteredImage=[]
            for i in range(self.greyImageArray.shape[0]):
                endpointVerical=i+medianKernelSize
                rowArray=[]
                for j in range(self.greyImageArray.shape[1]):
                    endPointHorizontal=j+medianKernelSize

                    #slice 3x3 array from the padded noise array
                    tempArray=numpy.array(padedNoisyImage[i:endpointVerical,j:endPointHorizontal])

                    #flat this 2d array then sort it
                    flattenArray=tempArray.flatten()
                    flattenSortedArray=self.Sort1DArrayAsc(flattenArray)#sort array from scratch ascendingly
                    n=len(flattenSortedArray)//2 #half of the array since the array will always have odd size since the kernel size is always odd
                    #flattenSortedArray=numpy.sort(flattenArray) #sort using numpy ascending order

                    #since the array is 3x3 then when flatten will yeild 9 1d array so the middle is in index 4
                    rowArray.append(flattenSortedArray[n])
                filteredImage.append(rowArray)

            # Convert the array to numy array then dar it    
            filteredImage=numpy.array(filteredImage) 
            self.drawSpatialFilterTab(3,filteredImage)

    def fourierdomainfunction(self):
        #there must be an image to resize the factor on it 
        try:
            assert len(self.greyImageArray)!=0
        except:
            self.messagebox("ERORR: Upload the image first then click on the same button again")
        else:
            self.drawInFourierdomainTab(0,self.greyImageArray) # Draw the original image array

            fft_image = numpy.fft.fftshift(numpy.fft.fft2(self.greyImageArray))
            fft_image_phase = numpy.arctan2(fft_image.imag,fft_image.real) # bytala3 radian
            fft_image_mag = numpy.sqrt(fft_image.real**2+fft_image.imag**2)
			

            # Apply log transformation method
            # c = 255 / numpy.log(1 + numpy.max(self.greyImageArray))
            # log_image = c * (numpy.log(self.greyImageArray + 1))

            fft_log_image_mag=numpy.log(fft_image_mag+1)
            fft_log_image_phase=numpy.log(fft_image_phase+2*math.pi)

            # fft_log_image = numpy.fft.fftshift(numpy.fft.fft2(log_image))
            # fft_log_image_phase = numpy.angle(fft_log_image)
            # fft_log_image_mag = numpy.abs(fft_log_image)
            
            self.drawInFourierdomainTab(1,fft_image_mag)
            self.drawInFourierdomainTab(2,fft_image_phase)
            self.drawInFourierdomainTab(3,fft_log_image_mag)
            self.drawInFourierdomainTab(4,fft_log_image_phase)


    def arrayNormalization(self,arr):
        # any value less than zero will be assigned as zero any value more than 255 will be assigned as 255
        normalizedarray=numpy.zeros((arr.shape[0],arr.shape[1]))
        for i in range(arr.shape[0]):
            for j in range(arr.shape[1]):
                if arr[i][j]>255:
                    normalizedarray[i][j]=255
                elif arr[i][j]<0:
                    normalizedarray[i][j]=0
                else:
                    normalizedarray[i][j]=arr[i][j]
        return normalizedarray

    # explicit function to normalize array
    def normalizeUsingEqn(self, arr, t_min, t_max):
        norm_arr = []
        diff = t_max - t_min
        diff_arr = np.max(arr) - np.min(arr)   
        for i in arr:
            temp = (((i - np.min(arr))*diff)/diff_arr) + t_min
            norm_arr.append(temp)
        return np.array(norm_arr)    

    def Sort1DArrayAsc(self,arr):
        #this sorting uses bubble sort of O(n^2) complexity
        #sorting the array ascendingly
        n = len(arr)
    
        # Traverse through all array elements
        for i in range(n):
    
            # Last i elements are already in place
            for j in range(0, n-i-1):
    
                # traverse the array from 0 to n-i-1
                # Swap if the element found is greater
                # than the next element
                if arr[j] > arr[j+1]:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
        return arr            

    def roundforRotation(self,x):
        frac,whole=math.modf(x)
        if (frac<=0.5):
            x=whole
        else:
            x=math.ceil(x)
        return x    

    def messagebox(self,x):    
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setText(x)
        msg.setWindowTitle('ERROR')
        msg.exec_()
    
    def draw_CreatedImage_noisefiltering(self):
        #picture of ones multiplied by 50 to ensure that the intensity is equal to 50
        self.drawnimage = np.ones((256, 256), dtype=np.float32)*50
        x_edge_for_grey = int(len(self.drawnimage) / 5)
        self.drawnimage[x_edge_for_grey:-x_edge_for_grey, x_edge_for_grey:-x_edge_for_grey] = 150  # gray square
        center = (int(len(self.drawnimage)/2), int(len(self.drawnimage)/2))
        radius = min(x_edge_for_grey, x_edge_for_grey, len(self.drawnimage)-center[0], len(self.drawnimage)-center[1])
        x, y = np.ogrid[:len(self.drawnimage), :len(self.drawnimage)]
        distance = np.sqrt((x - center[0])**2 + (y - center[0])**2)
        circle = distance <= radius
        self.drawnimage[circle] = 250
        self.ui.CreatedImage_NoiseFiltering_display.canvas.axes.clear()
        self.ui.CreatedImage_NoiseFiltering_display.canvas.axes.imshow(self.drawnimage,cmap="gray")    
        self.ui.CreatedImage_NoiseFiltering_display.canvas.draw()
    
    

    def added_noise_noisefiltering(self):

        #self.draw_CreatedImage_noisefiltering()
        #if gaussian
        if (self.ui.ChooseNoiseType_NoiseFIltering_comboBox.currentIndex()==2):
            #create an image with the same dimensions of the drawn image
            self.gaussian_noise = np.zeros((256, 256),dtype=np.uint8)
            #use random distribution to determine pixel value of the noise
            #self.gaussian_noise = cv2.randn(self.gaussian_noise, 0, 5) #correct
            self.gaussian_noise = numpy.random.normal(0,5,(256,256))
            #scale the noise
            #self.gaussian_noise = self.scale(self.gaussian_noise)
            #add the noise to the image
            self.noisy_gaussian_image = self.drawnimage + self.gaussian_noise
            #scale this image
            self.noisy_gaussian_image = self.scale(self.noisy_gaussian_image)
            final_saved_image = Image.fromarray((self.noisy_gaussian_image).astype(np.uint8))  
            final_saved_image.save('final_saved_image.jpeg') 
            #display the noisy_gaussian_image
            self.ui.ImageAfterNoise_NoiseFiltering_display.canvas.axes.clear()
            self.ui.ImageAfterNoise_NoiseFiltering_display.canvas.axes.imshow(self.noisy_gaussian_image,cmap="gray")    
            self.ui.ImageAfterNoise_NoiseFiltering_display.canvas.draw()


        #if uniform
        if (self.ui.ChooseNoiseType_NoiseFIltering_comboBox.currentIndex()==1):
            #create an image with the same dimensions of the drawn image
            self.uniform_noise = np.zeros((256, 256),dtype=np.uint8)
            #use random distribution to determine pixel value of the noise
            #self.uniform_noise = cv2.randu(self.uniform_noise, -10, 10)#Not Correct
            std=numpy.sqrt(((10+10)**2)/12)
            self.uniform_noise = numpy.random.uniform(-10,10,(256,256))#Not Correct
            #scale the noise
            #self.uniform_noise = self.scale(self.uniform_noise)
            #add the noise to the image
            self.noisy_uniform_image = self.drawnimage + self.uniform_noise
            #scale this image
            self.noisy_uniform_image = self.scale(self.noisy_uniform_image)
            final_saved_image = Image.fromarray((self.noisy_uniform_image).astype(np.uint8))  
            final_saved_image.save('final_saved_image.jpeg') 
            #display the noisy_uniform_image
            self.ui.ImageAfterNoise_NoiseFiltering_display.canvas.axes.clear()
            self.ui.ImageAfterNoise_NoiseFiltering_display.canvas.axes.imshow(self.noisy_uniform_image,cmap="gray")    
            self.ui.ImageAfterNoise_NoiseFiltering_display.canvas.draw()


    def ROI_region_select(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setText("- Select a ROI and then press SPACE or ENTER button!\n- Cancel the selection process by pressing c button!")
        msg.setWindowTitle('Attention')
        msg.exec_()
        #built in function to allow the user to choose ROI
        image_selected =cv2.imread("final_saved_image.jpeg")
        region = cv2.selectROI("Select The Area Desired", image_selected)
        self.selected_ROI_region = image_selected[int(region[1]):int(region[1]+region[3]),
                      int(region[0]):int(region[0]+region[2])]
        #show the selected_ROI_region
        self.ui.ImageAfterNoise_NoiseFiltering_display.canvas.axes.clear()
        self.ui.ImageAfterNoise_NoiseFiltering_display.canvas.axes.imshow(self.selected_ROI_region,cmap="gray")    
        self.ui.ImageAfterNoise_NoiseFiltering_display.canvas.draw()
        self.ROI_histogram()

    
    def ROI_histogram(self):
        #repeat histogram

        #self.ROIFrequencies=[]        
        # for k in range(0, 256):
        #     #Count the frequency of each intensity in the array
        #     count=0
        #     for i in range(self.selected_ROI_region.shape[0]):
        #         for j in range(self.selected_ROI_region.shape[1]):
        #             print(k,type(k),self.selected_ROI_region.shape[i][j][0],type(self.selected_ROI_region.shape[i][j][0]))
        #             # if (int(k)==int(self.selected_ROI_region.shape[i][j][0])):
        #             #     count = count +1

        #     #Append the intensity frequency in array of frequencies
        #     self.ROIFrequencies.append(count)

        self.ROIintensities=np.arange(0,256)
        self.ROIFrequencies=np.zeros(256)
        for i in range(self.selected_ROI_region.shape[0]):
            for j in range(self.selected_ROI_region.shape[1]):
                #last number is zero because the array of Selected ROI has 3 values in each element and all three are the same as the first
               self.ROIFrequencies[int(self.selected_ROI_region[i][j][0])]=  self.ROIFrequencies[int(self.selected_ROI_region[i][j][0])] +1

        probabilityOfintensitiesvalue = [x / (self.selected_ROI_region.shape[0]*self.selected_ROI_region.shape[1]) for x in self.ROIFrequencies]       
        mean=np.sum(self.ROIintensities*probabilityOfintensitiesvalue)
        standraddeviation=np.sqrt(np.sum(((self.ROIintensities-mean)**2)*probabilityOfintensitiesvalue))
        self.ui.ROIMean_NoiseFiltering_label_display.setText(str(np.round(mean,decimals=2)))
        self.ui.ROISD_NoiseFiltering_label_display.setText(str(np.round(standraddeviation,decimals=2)))

        self.ui.ROIHistogram_NoiseFiltering_display.canvas.axes.clear()
        self.ui.ROIHistogram_NoiseFiltering_display.canvas.axes.bar(self.ROIintensities,self.ROIFrequencies)   
        self.ui.ROIHistogram_NoiseFiltering_display.canvas.draw() 

    def backProjectionFunction(self):
        shepploganphantom=shepp_logan_phantom()
        shepploganphantom=rescale(shepploganphantom, scale=0.64, mode='reflect', channel_axis=None)#rescale it to 256x256
        self.drawInBackProjectionTab(0,shepploganphantom)
        allTheta = np.linspace(0., 180., max(shepploganphantom.shape), endpoint=False)
        sinogramOriginal = radon(shepploganphantom, theta=allTheta)
        self.drawInBackProjectionTab(1,sinogramOriginal)
        sinogramSpecifictheta = radon(shepploganphantom, theta=[0, 20, 40, 60,80,100,120,140,160])
        laminogramSpecifictheta = iradon(sinogramSpecifictheta, theta=[0, 20, 40, 60,80,100,120,140,160], filter_name = None)
        self.drawInBackProjectionTab(2,laminogramSpecifictheta)
        laminogramsllthetanofilter=iradon(sinogramOriginal, theta=allTheta, filter_name = None)
        self.drawInBackProjectionTab(3,laminogramsllthetanofilter)
        laminogramsllthetaRamLakfilter=iradon(sinogramOriginal, theta=allTheta, filter_name ="ramp")
        self.drawInBackProjectionTab(4,laminogramsllthetaRamLakfilter)
        laminogramsllthetaHammingfilter=iradon(sinogramOriginal, theta=allTheta, filter_name ="hamming")
        self.drawInBackProjectionTab(5,laminogramsllthetaHammingfilter)         

    def morphologicalFunction(self):
        if (len(self.binaryImageArray)==0):
            self.messagebox("upload the image first")
        elif (len(self.structuralElementArray)==0):
            self.messagebox("Enter the structural element size")     
        else:
            if (self.ui.chooseSEshape_Morphology_ComboBox.currentIndex()==0):
                print("Cross") 
                self.structuralElementArray[0][0]=0
                self.structuralElementArray[0][-1]=0
                self.structuralElementArray[-1][0]=0
                self.structuralElementArray[-1][-1]=0
            else:
                print("Square")    
            
            if (self.ui.chooseMorphologyType_Morphology_ComboBox.currentIndex()==0):
                self.messagebox("Choose the type of morphological operation")

            if (self.ui.chooseMorphologyType_Morphology_ComboBox.currentIndex()==1):
                ErosionedImage=self.ErosionMorphology(self.binaryImageArray)
                self.drawInMorphologyTab(1,ErosionedImage)
                print(ErosionedImage,ErosionedImage.shape)
            elif(self.ui.chooseMorphologyType_Morphology_ComboBox.currentIndex()==2):
                DilatatedImage=self.DilationMorphology(self.binaryImageArray)
                self.drawInMorphologyTab(1,DilatatedImage)
                print(DilatatedImage,DilatatedImage.shape)
            elif(self.ui.chooseMorphologyType_Morphology_ComboBox.currentIndex()==3):
                imageAfterOpening=self.OpeningMorphology(self.binaryImageArray)
                self.drawInMorphologyTab(1,imageAfterOpening)
                print(imageAfterOpening,imageAfterOpening.shape)
            elif(self.ui.chooseMorphologyType_Morphology_ComboBox.currentIndex()==4):
                imageAfterClosing=self.ClosingMorphology(self.binaryImageArray)
                self.drawInMorphologyTab(1,imageAfterClosing)
                print(imageAfterClosing,imageAfterClosing.shape)
            elif(self.ui.chooseMorphologyType_Morphology_ComboBox.currentIndex()==5):
                print("Inside Filter")
                #print(imageAfterOpening)
                imageAfterOpening=self.OpeningMorphology(self.binaryImageArray)
                imageAfterClosing=self.ClosingMorphology(imageAfterOpening)
                self.drawInMorphologyTab(1,imageAfterClosing)              

    def ErosionMorphology(self,array):

        padwidth=int((self.structuralElementArray.shape[0]-1)/2)
        matrix=array
        padedImage=numpy.zeros((int(array.shape[0])+padwidth*2,int(array.shape[1])+padwidth*2))
        padedImage[padwidth:int(array.shape[0])+padwidth,padwidth:int(array.shape[1]+padwidth)]+=matrix

        #initializing variables 
        ErosionedImage=[]
        for i in range(array.shape[0]):
            endpointVerical=i+self.structuralElementArray.shape[0]
            rowArray=[]
            for j in range(array.shape[1]):
                endPointHorizontal=j+self.structuralElementArray.shape[1]

                #This row will take each 3x3 array from the padedimage and multiply image by kernel element byb element and then sum all the elements after multipling
                rowArray.append(self.FITINMorphology(padedImage[i:endpointVerical,j:endPointHorizontal],self.structuralElementArray))
                #rowArray.append(np.min(self.MultBitWiseE(padedImage[i:endpointVerical,j:endPointHorizontal],self.structuralElementArray)))
            ErosionedImage.append(rowArray)
        ErosionedImage=numpy.array(ErosionedImage)
        return ErosionedImage


    def DilationMorphology(self,array):
        
        padwidth=int((self.structuralElementArray.shape[0]-1)/2)
        matrix=array
        padedImage=numpy.zeros((int(array.shape[0])+padwidth*2,int(array.shape[1])+padwidth*2))
        padedImage[padwidth:int(array.shape[0])+padwidth,padwidth:int(array.shape[1]+padwidth)]+=matrix

        #initializing variables 
        DilatatedImage=[]
        for i in range(array.shape[0]):
            endpointVerical=i+self.structuralElementArray.shape[0]
            rowArray=[]
            for j in range(array.shape[1]):
                endPointHorizontal=j+self.structuralElementArray.shape[1]

                #This row will take each 3x3 array from the padedimage and multiply image by kernel element byb element and then sum all the elements after multipling
                rowArray.append(self.HITINMorphology(padedImage[i:endpointVerical,j:endPointHorizontal],self.structuralElementArray))
                #rowArray.append(np.max(self.MultBitWiseD(padedImage[i:endpointVerical,j:endPointHorizontal],self.structuralElementArray)))
            DilatatedImage.append(rowArray)
        DilatatedImage=numpy.array(DilatatedImage)
        return DilatatedImage

    def OpeningMorphology(self,array):
        ErosionedImage=self.ErosionMorphology(array)
        DilatatedImage=self.DilationMorphology(ErosionedImage)
        return DilatatedImage

    def ClosingMorphology(self,array):
        DilatatedImage=self.DilationMorphology(array)
        ErosionedImage=self.ErosionMorphology(DilatatedImage)
        return ErosionedImage

    def HITINMorphology(self,imageArray,StructuralElement):
        if (imageArray.shape[0]==StructuralElement.shape[0]):
            # for i in range(imageArray.shape[0]):
            #     for j in range(imageArray.shape[0]):
            #         if ((StructuralElement[i][j]==1) and imageArray[i][j]==1):
            #             return 1
            # return 0 #if not found
            if((np.sum(np.multiply(StructuralElement,imageArray)))>=1):
                return 1
            else:
                return 0
        else:
            print("Both Must be of the same size")

    def FITINMorphology(self,imageArray,StructuralElement):
        if (imageArray.shape[0]==StructuralElement.shape[0]):
                #subtractedArray=StructuralElement-imageArray
                multiplicatedArray=StructuralElement*imageArray
                subtractedArray=multiplicatedArray-StructuralElement
                if (np.sum(subtractedArray)==0):
                    return 1
                else:
                    return 0    
        else:
            print("Both Must be of the same size")

    # def FITINMorphology(self,imageArray,StructuralElement):
    #     result = np.zeros(imageArray.shape)
    #     for i in range(imageArray.shape[0]):
    #         for j in range(imageArray.shape[1]):
    #             if (StructuralElement[i][j]==0):
    #                 result[i][j]=1
    #             else:
    #                 result[i][j] = StructuralElement[i][j] * imageArray[i][j]    
    #     return result


    # def MultBitWiseE(self,Mat1:np.ndarray,Mat2:np.ndarray):
    #     result=np.zeros(Mat1.shape)
    #     for i in range (Mat1.shape[0]):
    #         for j in range(Mat1.shape[1]):
    #             if Mat2[i][j] == 0 :
    #                 result[i][j]=255
    #             else:
    #                 result[i][j]=Mat1[i][j]*Mat2[i][j]
    #     return result

    # def MultBitWiseD(self,Mat1:np.ndarray,Mat2:np.ndarray):
    #     result=np.zeros(Mat1.shape)
    #     for i in range (Mat1.shape[0]):
    #         for j in range(Mat1.shape[1]):
    #             if Mat2[i][j] ==0 :
    #                 result[i][j]=0
    #             else:
    #                 result[i][j]=Mat1[i][j]*Mat2[i][j]
    #     return result
          


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet())
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())        