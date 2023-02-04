# ImageProcessing_Application
 This python app will visualize most of image processing operations that might be done on an image such as opening, closing, back projection and many more

##Tab1 (Image Loading)
I was required to create a GUI that allows the user to browse for and display a:
1. DICOM image
2. JPEG image
3. BMP image

The GUI must also display the following information besides the image:
1. Image width and height (number of rows and number of columns)
2. Image total size in bits 
3. Bit depth (bit/pixel)
4. Image color (RGB, grayscale, binary)
5. For a DICOM image, display all the above AND:
• Modality used (US, CT, MR…) [Standard name: Modality]
• Patient name [Standard name: PatientName]
• Patient Age [Standard name: PatientAge]
• Body part examined [Standard name: BodyPartExamined]

##Tab2 (Zooming)
1. After browsing for an image, if the image is in RGB then transform it to grayscale
2. In a new tab:
a. Display a zoomed version of that image using a zooming factor input by the user
from a textbox
b. You should display 2 zoomed versions of the original image using 2 different 
interpolation methods:
i. Nearest-neighbor interpolation
ii. Linear interpolation
3. You are not allowed to use built-in libraries for interpolation. The code should be written 
from scratch

##Tab3 (Transformation)
The user will be inputting the angle, The canvas should contain an axis to view the image 
dimension and a text box viewing the angle and direction 
i.e.: 30 degrees Left if he inputted 30 “since our convention is anticlockwise"
and Shear the image 45 deg right and left

Note: When Entering the Size Factor Enter it and press "ENTER" Button to show you the image

#video 1 shows the first three tabs

https://user-images.githubusercontent.com/73857229/216762790-abefa307-6563-4706-a312-e301cead5192.mp4

##Tab4 (Histogram Equalization)
make histogram equalization on the image

##Tab5 (Spatial Filtering)
1. Display the image 
2. Perform un-sharp masking 
a. You will need to create a box filter. Kernel size: USER INPUT 
b. You will need to implement a 2D convolution function that convolves the 
kernel with the image (from scratch). Note: Use padding 
c. You will need to subtract blurred image from original 
d. The result of ‘c’ will be multiplied by a factor K: USER INPUT. Then 
added to the original image 
e. The result of d is the enhanced image 
3. Display enhanced image 
Note: The result can have negative values; you should implement a scaling 
function so the displayed result will be in the range 0-255 for an 8-bit image. 
Bonus: Add salt and pepper noise to the image, display the noisy image, then use 
the proper spatial filter to remove the noise and display the de-noised image.

##Tab6 (Fourier Domain)
after browsing for an image you are required to:
1. Display the image
2. Apply Fourier transform to the image
3. Display the magnitude and the phase of the Fourier transformed image
a. You will need to use fft and fftshift 
b. You will need to perform log for the display of magnitude image
c. You will need to use scaling for display

##Tab7 (Fourier Filtering)
in this tab we are trying to check how effitient is the fourier filtering so we have made the filter and then subtract it from the spatial to check if there is any diff, since the diff is mostly black image so both filterings yeilds very similar data
And then remove the Periodic noise from the image using notch filter

#video 2 shows tabs 4,5,6,7


https://user-images.githubusercontent.com/73857229/216763334-3ceafbeb-197a-4976-9f49-5f5404de1237.mp4
![image](https://user-images.githubusercontent.com/73857229/216763852-6996fa20-fe5e-4944-af59-63a14d48e6f2.png)

##Tab8 (Noise Filtering)
get the noise in chosen ROI

##Tab9 (Back Projection)
Viewing Phantom in all angles and views

##Tab10 (morphlogical operations)
Apply Opening, closing, Dilation, Erosion and Filtering on all black and white images provided according to kernel size given by the 

https://user-images.githubusercontent.com/73857229/216764194-a782be1c-1da3-4dfa-a94f-77934b73f9a5.mp4

user and kernel shape chosen by the user


