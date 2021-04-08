import os
from collections import defaultdict

import cv2
import pandas

import pydicom
import imageio
from skimage import img_as_int, img_as_ubyte
from skimage import exposure
df = pandas.read_excel(open(r'C:\Users\Julia Scott\Desktop\Varian 2020_2021\Prashul\Excel\OralCavityImages_Subset.xlsx', 'rb'),sheet_name='Sheet1')


# # Training Samples
dict = defaultdict(list)
# dict -> filepath -> [26,40] where startSlice = 26 and endSlice = 40
for i in df.index:
    try:
        startSlice = int(df['Start Slice'][i])
        endSlice = int(df['End Slice'][i])
        fileLocation = df['File Location'][i]
        # print(str(startSlice) + "," + str(endSlice) + "   " + fileLocation)
        dict[fileLocation].append(startSlice)
        dict[fileLocation].append(endSlice)
    except ValueError:
        continue

all_filenames = []
# all_filenames = ["\PatientId\1-026.dcm","\PatientId\1-027dcm","\PatientId\1-028.dcm",..."\PatientId\1-040.dcm",]
for folderPath in dict:
    startSlice = dict[folderPath][0]
    endSlice = dict[folderPath][1]
    sliceNo = startSlice
    while sliceNo <= endSlice:
        dcmFileName = "1-" + str(sliceNo).zfill(3) + ".dcm"
        jpgFileName=  "1-" + str(sliceNo).zfill(3) + ".jpg"
        print( dcmFileName )
        print( jpgFileName )
        dcmFilePath = os.path.join(folderPath, dcmFileName)
        jpgFilePath = os.path.join(folderPath, jpgFileName)
        ds = pydicom.read_file(dcmFilePath,force=True)
        img = ds.pixel_array  # extract image information
        image = exposure.equalize_adapthist(img)
        # cv2.imshow("dicom", image)
        # cv2.waitKey(0)
        imageio.imsave(jpgFilePath, img_as_ubyte(image))
        sliceNo = sliceNo + 1


# Test Samples




testFolderPath = r'C:\Users\Julia Scott\Desktop\Varian 2020_2021\Prashul\jpeg\Test_Lossy'
test_Images_path = os.listdir(testFolderPath)
for n, image in enumerate(test_Images_path):
    if image.endswith(".dcm"):
        dcmFilePath = os.path.join(testFolderPath,image)
        fileName = os.path.splitext(image)[0]
        jpgFilePath =  os.path.join(testFolderPath,fileName + ".jpg" )
        print( dcmFilePath )
        print( jpgFilePath )
        ds = pydicom.read_file(dcmFilePath,force=True)
        img = ds.pixel_array  # extract image information
        image = exposure.equalize_adapthist(img)
        # cv2.imshow("dicom", image)
        # cv2.waitKey(0)
        imageio.imsave(jpgFilePath, img_as_ubyte(image))