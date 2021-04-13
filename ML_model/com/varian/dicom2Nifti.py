
# import os
#
# command = 'python med2image -i "C:\\Users\\Julia Scott\\Desktop\\Varian 2020_2021\\Prashul\\jpeg\\dcm\\1-002.dcm" -d  "C:\\Users\\Julia Scott\\Desktop\\Varian 2020_2021\\Prashul\\jpeg\\dcm"'
# inputFilePath = "E:\\Users\\Julia Scott\\Desktop\\Varian 2020_2021\\Prashul\\jpeg\\dcm\\1-002.dcm"
# outputFilePath = "E:\\Users\\Julia Scott\\Desktop\\Varian 2020_2021\\Prashul\\jpeg\\dcm\\1-002_new.jpg"
# command = 'python '  + '"' + "C:\\Users\\Julia Scott\\AppData\\Roaming\\Python\\Python36\\Scripts\\med2image.py" + '"' + ' -i ' + '"' + inputFilePath + '"' + ' -d out ' + '"' + outputFilePath + '" '
# print( command )
# os.system( command )
# print("Executed")

# import numpy as np
# import png, os, pydicom

# source_folder = 'C:\\Users\\Julia Scott\\Desktop\\Varian 2020_2021\\Prashul\\jpeg\\dcm'
# output_folder = r'C:\\Users\\Julia Scott\\Desktop\\Varian 2020_2021\\Prashul\\png'
#
#
# def dicom2png(source_folder, output_folder):
#     list_of_files = os.listdir(source_folder)
#     for file in list_of_files:
#         try:
#             ds = pydicom.dcmread(os.path.join(source_folder,file))
#             shape = ds.pixel_array.shape
#
#             # Convert to float to avoid overflow or underflow losses.
#             image_2d = ds.pixel_array.astype(float)
#
#             # Rescaling grey scale between 0-255
#             image_2d_scaled = (np.maximum(image_2d,0) / image_2d.max()) * 255.0
#
#             # Convert to uint
#             image_2d_scaled = np.uint8(image_2d_scaled)
#
#             # Write the PNG file
#             with open(os.path.join(output_folder,file)+'.png' , 'wb') as png_file:
#                 w = png.Writer(shape[1], shape[0], greyscale=True)
#                 w.write(png_file, image_2d_scaled)
#         except:
#             print('Could not convert: ', file)
#
#
# dicom2png(source_folder, output_folder)
import monai
monai.config.print_config()
