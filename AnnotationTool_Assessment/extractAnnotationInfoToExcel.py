import os
import sys
from collections import defaultdict
from collections import Counter
from xlwt import Workbook

import pandas
from pandas import ExcelWriter

annotatorIntials = ['_JS', '_PS', '_DH', '_ST']
mapOfFoldersAnnotatorsInfo = defaultdict(lambda: [0] * len(annotatorIntials))
errorInfo = []
mapOfAgreementsInfo = defaultdict(lambda: [0] * 3)
inputExcelSheetName = 'Phase C'


def validInputParameters(sysArguments):
    length = len(sysArguments.argv)
    print('Arguments passed ', length)

    if length == 3:
        return True
    return False


if not validInputParameters(sys):
    print('Invalid arguments')
    sys.exit(0)


def readCSVFiles(csvFolderPath, patientId, mapOfFoldervsAnnotatorsInfo):
    for i in range(len(annotatorIntials)):
        annotatorFileName = patientId + annotatorIntials[i] + ".csv"
        try:
            csvInfo = pandas.read_csv(os.path.join(csvFolderPath, annotatorFileName), sep=',')
        except IOError as e:
            errorInfo.append(" Annotator file missing " + os.path.join(csvFolderPath, annotatorFileName))
            continue
        for index, fileInfo in csvInfo.iterrows():
            indexValue = 1
            fileLocation = fileInfo[0]
            imageLabel = fileInfo[1]

            if fileLocation.find(csvFolderPath) == -1:
                errorInfo.append("Folder column mismatch , Expecting " + csvFolderPath + " " + annotatorFileName)
                break

            if imageLabel == 'medium':
                indexValue = 2
            elif imageLabel == 'high':
                indexValue = 3
            elif imageLabel == 'excluded':
                continue
            mapOfFoldersAnnotatorsInfo[fileLocation][i] = indexValue


def getListOfFolder(excelFilePath):
    input_excel_data_df = pandas.read_excel(excelFilePath, sheet_name=inputExcelSheetName)
    # Get all the folder path specified under FILE_LOCATION column header
    return input_excel_data_df[['FILE_LOCATION', 'PATIENT_ID']]


print('Input Directory name :', str(sys.argv[1]))
print('Output file path name :', str(sys.argv[2]))
excelInputFilePath = str(sys.argv[1])
outputExcelFilePath = str(sys.argv[2])
inputExcelData = getListOfFolder(excelInputFilePath)
mapOfFoldervsAnnotatorsInfo = defaultdict(list)
for ind in inputExcelData.index:
    readCSVFiles(inputExcelData['FILE_LOCATION'][ind], inputExcelData['PATIENT_ID'][ind], mapOfFoldervsAnnotatorsInfo)

for key, value in mapOfFoldersAnnotatorsInfo.items():
    agreementInfo = Counter(value)
    if 1 in agreementInfo:
        mapOfAgreementsInfo[key][0] = agreementInfo[1]
    if 2 in agreementInfo:
        mapOfAgreementsInfo[key][1] = agreementInfo[2]
    if 3 in agreementInfo:
        mapOfAgreementsInfo[key][2] = agreementInfo[3]

print(mapOfAgreementsInfo)
# print( mapOfFoldersAnnotatorsInfo )
# pandasDataFrame =  pandas.DataFrame.from_dict(mapOfFoldersAnnotatorsInfo)
# pandasDataFrame = pandasDataFrame.T
# df = pandasDataFrame
df = pandas.DataFrame(mapOfFoldersAnnotatorsInfo).reset_index()
df = df.transpose()
df = df.fillna(0)
# df = pandas.DataFrame(pandas.np.empty((0, 4)))
df.columns = ["RATER JS", "RATER PS", "RATER DH", "RATER ST"]
writer = ExcelWriter(outputExcelFilePath)

df.to_excel(writer, sheet_name="Ratings_Info")
ndf = pandas.DataFrame(errorInfo)
ndf.to_excel(writer, sheet_name="Error_Info")

ddf = pandas.DataFrame(mapOfAgreementsInfo).reset_index()
ddf = ddf.transpose()
ddf = ddf.fillna(0)
ddf.columns = ["Low", "Medium", "High"]
ddf.to_excel(writer, sheet_name="Agreement_Info")
excel_file_path = str(sys.argv[2])
writer.save()
