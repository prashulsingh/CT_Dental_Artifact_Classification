import os
from collections import defaultdict
import pandas
from PIL import Image
import imageio

df = pandas.read_excel(open(r'C:\Users\Julia Scott\Desktop\Varian 2020_2021\Prashul\Excel\OralCavityImages_Subset.xlsx', 'rb'),
                       sheet_name='Sheet1')

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
sliceNo=0
for folderPath in dict:
    startSlice = dict[folderPath][0]
    endSlice = dict[folderPath][1]
    while startSlice <= endSlice:
        fileName = "1-" + str(startSlice).zfill(3)
        jpgFilePath = os.path.join(folderPath, fileName+".jpg")
        image_RGB = Image.open(jpgFilePath)
        image_L = image_RGB.convert("L")
        print( jpgFilePath )
        print( type( image_L))
        imageio.imsave(jpgFilePath, image_L)
        startSlice = startSlice + 1