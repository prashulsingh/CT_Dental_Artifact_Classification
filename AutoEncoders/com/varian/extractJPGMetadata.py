from PIL import Image
from PIL.ExifTags import TAGS
import imageio
from collections import defaultdict
import pandas
import os

imagename = r'C:\Users\Julia Scott\Desktop\Varian 2020_2021\Prashul\jpeg\Test3\1-090.jpg'


print(type(imagename))
image = Image.open(imagename)
# read the image data using PIL
print(image)
# read the image data using PIL
print(type(image))


# using convert method for img1
img1 = image.convert("L")
# img1.show()
# imageio.imsave(imagename, img1)


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
        print( jpgFilePath )
        image = Image.open(jpgFilePath)
        print(image.mode)
        startSlice = startSlice + 1