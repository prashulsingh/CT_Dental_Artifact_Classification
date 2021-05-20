import os
import pydicom

#  Read folders which have dicom files
root_dir_path = '/Users/prashulsingh/CodeBase/varian/Patient1_Data'
dir_paths = []
for root, subdirs, files in os.walk(root_dir_path):
    if len(files) > 0:
        dir_paths.append(root)

print(dir_paths)
parallel_dir_name = "parallel"

map_dir_to_sorted_files = dict()
for dir_path in dir_paths:
    print(dir_path)
    slices = [pydicom.dcmread(dir_path + '/' + s, force=True) for s in os.listdir(dir_path)]
    slices = [s for s in slices if 'SliceLocation' in s]
    #  Sort those dcm files using dcm sort functionality
    slices.sort(key=lambda x: int(x.InstanceNumber))
    index = 0
    listOfFolders = dir_path.split(os.path.sep)
    listOfFolders = listOfFolders[1:]
    listOfFolders[3] = parallel_dir_name
    parallel_directory_path = "/"+os.path.join(*listOfFolders)
    print(parallel_directory_path)
    os.makedirs(parallel_directory_path,exist_ok=True)
    for s in slices:
        fileName = os.path.splitext( os.path.split(s.filename)[1] )[0]
        ordered_file_name = fileName + "_" + str(index) + ".dcm"
        file_path = os.path.join(parallel_directory_path, ordered_file_name)
        print(file_path)
        # Step4 -> Save the files into the parallel folder
        pydicom.dcmwrite(file_path, s)
        index = index + 1