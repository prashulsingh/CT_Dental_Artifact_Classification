from collections import defaultdict

import pandas
import os
import pydicom as dicom
import cv2

df = pandas.read_excel(open(r'C:\Users\Julia Scott\Desktop\Varian 2020_2021\Prashul\Excel\OralCavityImages.xlsx', 'rb'),
                       sheet_name='Sheet1')

dict = defaultdict(list)

for i in df.index:
    try:
        startSlice = int(df['Start Slice'][i])
        endSlice = int(df['End Slice'][i])
        fileLocation = df['File Location'][i]
        print(str(startSlice) + "," + str(endSlice) + "   " + fileLocation)
        dict[fileLocation].append(startSlice)
        dict[fileLocation].append(endSlice)
    except ValueError:
        continue

for folderPath in dict:
    startSlice = dict[folderPath][0]
    endSlice = dict[folderPath][1]
    sliceNo = startSlice
    while sliceNo <= endSlice:
        fileName = "1-" + str(sliceNo).zfill(3) + ".dcm"
        jpegFileName = "1-" + str(sliceNo).zfill(3) + ".jpeg"
        jpgFileName = "1-" + str(sliceNo).zfill(3) + ".jpg"
        ds = dicom.dcmread(os.path.join(folderPath, fileName), force=True)
        pixel_array_numpy = ds.pixel_array
        cv2.imwrite(os.path.join(folderPath, jpgFileName), pixel_array_numpy)
        os.remove(os.path.join(folderPath, jpegFileName))
        sliceNo = sliceNo + 1
