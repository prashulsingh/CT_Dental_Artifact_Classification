from PIL import Image

from collections import defaultdict
import pandas
import os


def get_num_pixels(filepath):
    width, height = Image.open(filepath).size
    if width*height != 262144:
        print( width*height )
    return width*height








df = pandas.read_excel(open(r'C:\Users\Julia Scott\Desktop\Varian 2020_2021\Prashul\Excel\OralCavityImages.xlsx', 'rb'),
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

all_filenames = []
# all_filenames = ["\PatientId\1-026.dcm","\PatientId\1-027dcm","\PatientId\1-028.dcm",..."\PatientId\1-040.dcm",]
for folderPath in dict:
    startSlice = dict[folderPath][0]
    endSlice = dict[folderPath][1]
    sliceNo = startSlice
    while sliceNo <= endSlice:
        jpgFileName = "1-" + str(sliceNo).zfill(3) + ".jpg"
        get_num_pixels(os.path.join(folderPath, jpgFileName))
        sliceNo = sliceNo + 1