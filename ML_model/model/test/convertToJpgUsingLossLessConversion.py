import os
from collections import defaultdict
import pandas


# python med2image -i \"C:\\Users\\Julia Scott\\Desktop\\Varian 2020_2021\\Prashul\\jpeg\\dcm - Copy\\1-002.dcm\" -d \"C:\\Users\\Julia Scott\\Desktop\\Varian 2020_2021\\Prashul\\jpeg\\dcm-cop2\"
# python med2image -i \"C:\\Users\\Julia Scott\\Desktop\\Varian 2020_2021\\Prashul\\jpeg\\dcm - Copy\\1-002.dcm\" -d \"C:\\Users\\Julia Scott\\Desktop\\Varian 2020_2021\\Prashul\\jpeg\\dcm-cop2\"
# python med2image -i \"C:\\Users\\Julia Scott\\Desktop\\Varian 2020_2021\\Prashul\\jpeg\\dcm - Copy\\1-002.dcm\" -d \"C:\\Users\\Julia Scott\\Desktop\\Varian 2020_2021\\Prashul\\jpeg\\dcm-cop2\"
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

f = open(r'C:\Users\Julia Scott\Desktop\Varian 2020_2021\Prashul\dcm2Jpeg_Subset.sh', "w")
pythonpath = r'C:\Users\Julia Scott\AppData\Roaming\Python\Python36\Scripts'
f.write("cd  " + "\"" + pythonpath + "\"" + "\n" )

sliceNo=0
for folderPath in dict:
    startSlice = dict[folderPath][0]
    endSlice = dict[folderPath][1]
    while startSlice <= endSlice:
        fileName = "1-" + str(startSlice).zfill(3)
        dcmFilePath = os.path.join(folderPath, fileName+".dcm")
        jpegFolderPath = folderPath
        f.write("python med2image -i " + "'" +dcmFilePath + "'" +  " -d " + "'" +jpegFolderPath + "'" + " --convertOnlySingleDICOM  --outputFileStem " + '"' + fileName +".jpg" + '"' + "\n" )
        startSlice = startSlice + 1




## reading the test images



all_testNames = []
# all_testNames = ["\PatientId\1-026.dcm","\PatientId\1-027dcm","\PatientId\1-028.dcm",..."\PatientId\1-040.dcm",]
testFolderPath = r'C:\Users\Julia Scott\Desktop\Varian 2020_2021\Prashul\jpeg\Test_Lossless'
test_Images_path = os.listdir(testFolderPath)
pythonpath = r'C:\Users\Julia Scott\AppData\Roaming\Python\Python36\Scripts'
f = open(r'C:\Users\Julia Scott\Desktop\Varian 2020_2021\Prashul\testDcm2Jpeg.sh', "w")
f.write("cd  " + "\"" + pythonpath + "\"" + "\n" )

for n, image in enumerate(test_Images_path):
    if image.endswith(".dcm"):
        dcmFilePath = os.path.join(testFolderPath, image)
        jpegFolderPath = testFolderPath
        # >>> os.path.splitext(base)
        # ('file', '.ext')
        # >>> os.path.splitext(base)[0]
        # 'file'
        fileName = os.path.splitext(image)[0]
        f.write("python med2image -i " + "'" + dcmFilePath + "'" + " -d " + "'" + jpegFolderPath + "'" + " --convertOnlySingleDICOM  --outputFileStem " + '"' + fileName + ".jpg" + '"' + "\n")



