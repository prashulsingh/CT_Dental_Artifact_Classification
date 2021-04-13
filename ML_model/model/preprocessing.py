import pandas
import glob
import pydicom as dicom
import numpy as np


class preprocessing:
    annotationExcelInfo = r'C:\Users\Julia Scott\Desktop\Varian 2020_2021\Prashul\TrainDataset_Subset.xlsx'
    filePaths = []
    category = []
    dcmValues = []
    excludedFilePath = []

    def getFilePaths(self, sheet_name='ALL'):
        # Excel file contain info about the oral cavity images / Used to train the model
        df = pandas.read_excel(open(self.annotationExcelInfo, 'rb'), sheet_name=sheet_name)
        return df['File Location']

    def readCSVInfo(self, annotation_file_paths):
        for file_path in annotation_file_paths:
            csv_files = glob.glob(file_path + "/*.csv")
            # print(csv_files)
            if len(csv_files) == 0:
                print(file_path, "Error -> CSV files missing")
                continue
            # take first csv files
            header_list = ["filePath", "artifactLevel"]
            df = pandas.read_csv(csv_files[0], names=header_list)
            grouped_df = df.groupby(by="artifactLevel")
            gb = grouped_df.groups

            for key, item in grouped_df:
                item_df = item['filePath']
                if key == 'excluded':
                    self.excludedFilePath.extend(item_df)
                    # Dont include images labelled as excluded
                    continue
                if key == 'low ':
                    key = 0
                elif key == 'medium':
                    key = 1
                elif key == 'high':
                    key = 2
                self.category.extend([key for i in range(len(item_df))])
                self.filePaths.extend(item_df)

    def loadDicomFiles(self):
        for filePath in self.filePaths:
            pixel_array_numpy = dicom.dcmread(filePath).pixel_array
            self.dcmValues.append(pixel_array_numpy)

    def getImages(self):
        # read annotation file path from excel
        annotation_file_paths = self.getFilePaths()
        # read CSV files
        self.readCSVInfo(annotation_file_paths)
        count = 0
        print("file Path size ", len(self.filePaths))
        print("Category size", len(self.category))
        self.loadDicomFiles()
        print(np.shape(self.dcmValues[0]))
        X = np.asarray(self.dcmValues)
        print(X.shape)
        X = X.reshape(X.shape[0], X.shape[1], X.shape[2], 1)
        print(X.shape)
        print(len(self.category))
        print(self.category)
        low = 0
        high = 0
        medium = 0
        for i in self.category:
            if i == 0:
                low += 1
            elif i == 1:
                medium += 1
            elif i == 2:
                high += 1
        print('-------------------')
        print('low', low)
        print('high', high)
        print('medium', medium)
        print('excluded',len(self.excludedFilePath))
        return X, np.asarray(self.category)

