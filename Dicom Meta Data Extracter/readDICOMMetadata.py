#!/usr/bin/env python

# !/usr/bin/env python


import SimpleITK as sitk
import os
import sys
from collections import defaultdict

from xlwt import Workbook


def initialize_reader(filePath):
    reader = sitk.ImageFileReader()
    reader.SetFileName(filePath)
    reader.LoadPrivateTagsOn()
    reader.ReadImageInformation()
    reader.SetFileName(filePath)
    reader.LoadPrivateTagsOn()
    reader.ReadImageInformation()
    return reader


def getAllDicomFiles():
    hash_map = defaultdict(list)
    for subdir, dirs, files in os.walk(folderPath):
        for filename in files:
            file_path = subdir + os.sep + filename
            folder_structure = file_path[0:file_path.rindex('\\')]
            if not filename.endswith('.dcm'):  # to read only dicom files
                continue
            if filename.endswith('.dcm'):
                if len(hash_map[folder_structure]) == 0:
                    hash_map[folder_structure].append(0)
                    hash_map[folder_structure].append(filename)
                else:
                    hash_map[folder_structure][0] += 1
                continue

    return hash_map


def write_to_excel(sheet, wb):
    hash_map = getAllDicomFiles()
    i = 0
    # https://www.dicomlibrary.com/dicom/dicom-tags/ refer to this for tag values
    dicomTagValues = []
    dicomTagValues.append([PATIENT_ID, '0010|0020'])
    dicomTagValues.append([STUDY_DESCRIPTION, '0008|1030'])
    dicomTagValues.append([SERIES_DATE, '0008|0021'])
    dicomTagValues.append([SERIES_DESCRIPTION, '0008|103E'])
    dicomTagValues.append([BODY_PART_EXAMINED, '0018|0015'])
    dicomTagValues.append([IMAGE_TYPE, '0008|0008'])
    dicomTagValues.append([PATIENT_POS, '0018|5100'])
    dicomTagValues.append([ORIENTATION, '0020|0037'])
    dicomTagValues.append([SLICE_THICKNESS, '0018|0050'])
    dicomTagValues.append([PIXEL_SPACING, '0028|0030'])
    # User derivedInfo
    dicomTagValues.append([FILE_LOCATION, ''])
    dicomTagValues.append([NO_OF_STACK_IMAGES, ''])

    for folder in hash_map:
        file_name = hash_map[folder][1]
        reader = initialize_reader(os.path.join(folder, file_name))
        for dicomTagValue in dicomTagValues:
            if dicomTagValue[0] == FILE_LOCATION:
                sheet.write(i + 1, dicomTagValue[0], folder)
                continue
            if dicomTagValue[0] == NO_OF_STACK_IMAGES:
                sheet.write(i + 1, dicomTagValue[0], hash_map[folder][0])
                continue
            try:
                sheet.write(i + 1, dicomTagValue[0], str(reader.GetMetaData(dicomTagValue[1])).strip())  # Patient ID
            except KeyError:
                pass
            except RuntimeError:
                pass
        i = i + 1

        wb.save(excel_file_path)


PATIENT_ID = 0
STUDY_DESCRIPTION = 1
SERIES_DATE = 2
SERIES_DESCRIPTION = 3
BODY_PART_EXAMINED = 4
IMAGE_TYPE = 5
PATIENT_POS = 6
ORIENTATION = 7
SLICE_THICKNESS = 8
PIXEL_SPACING = 9
NO_OF_STACK_IMAGES = 10
FILE_LOCATION = 11


def create_work_book():
    # Workbook is created
    wb = Workbook()
    # Writing to an excel
    # sheet using Python
    # Workbook is created
    wb = Workbook()
    # add_sheet is used to create sheet.
    excel_header = []
    excel_header.append('PATIENT_ID')
    excel_header.append('STUDY_DESCRIPTION')
    excel_header.append('SERIES_DATE')
    excel_header.append('SERIES_DESCRIPTION')
    excel_header.append('BODY_PART_EXAMINED')
    excel_header.append('IMAGE_TYPE')
    excel_header.append('PATIENT_POS')
    excel_header.append('ORIENTATION')
    excel_header.append('SLICE_THICKNESS')
    excel_header.append('PIXEL_SPACING')
    excel_header.append('NO_OF_STACK_IMAGES')
    excel_header.append('FILE_LOCATION')

    new_sheet = wb.add_sheet('Sheet 1')
    for i in range(0, len(excel_header)):
        new_sheet.write(0, i, excel_header[i])
    return new_sheet, wb


def validInputParameters(sys):
    length = len(sys.argv)
    print('Argumements passed ', length)

    if length == 3:
        return True
    return False


if not validInputParameters(sys):
    print('Invalid Argumements')
    sys.exit(0)

print('Input Directory name :', str(sys.argv[1]))
print('Output file path name :', str(sys.argv[2]))
folderPath = str(sys.argv[1])
sheet, wb = create_work_book()
excel_file_path = str(sys.argv[2])
# collectionNames = os.listdir(folderPath)
# print(collectionNames)
write_to_excel(sheet, wb)
getAllDicomFiles()
print('****Metadata extraction completed****')
print('Excel file created at', excel_file_path)
