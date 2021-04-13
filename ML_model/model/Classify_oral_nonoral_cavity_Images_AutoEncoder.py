import logging
import sys
import random
import pydicom
import numpy as np
from tqdm import trange
import matplotlib.pyplot as plt
import torch
import itk
from collections import defaultdict
import pandas
import os
from monai.data import CacheDataset, DataLoader
from monai.networks.nets import AutoEncoder
from monai.utils import set_determinism

from monai.transforms import (
    AddChannelD,
    Compose,
    LoadImageD,
    RandFlipD,
    RandRotateD,
    RandZoomD,
    ScaleIntensityD,
    ToTensorD,
    Lambda,
)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
set_determinism(0)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Small visualisation function
def plot_ims(ims, shape=None, figsize=(20, 20), titles=None):
    shape = (1, len(ims)) if shape is None else shape
    plt.subplots(*shape, figsize=figsize)
    for i, im in enumerate(ims):
        plt.subplot(*shape, i + 1)
        im = plt.imread(im) if isinstance(im, str) else torch.squeeze(im)
        plt.imshow(im, cmap='gray')
        if titles is not None:
            plt.title(titles[i])
        plt.axis('off')
    plt.tight_layout()

    plt.show()


# Excel file contain info about the oral cavity images / Used to train the model
df = pandas.read_excel(
    open(r'C:\Users\Julia Scott\Desktop\Varian 2020_2021\Prashul\Excel\OralCavityImages.xlsx', 'rb'),
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
        all_filenames.append(os.path.join(folderPath, jpgFileName))
        sliceNo = sliceNo + 1

# testFile name contains the location of all the images apart from the trainig fed to the autoencoder
all_testNames = []
testFolderPath = r'C:\Users\Julia Scott\Desktop\Varian 2020_2021\Prashul\jpeg\Test3'
test_Images_path = os.listdir(testFolderPath)
for n, image in enumerate(test_Images_path):
    if not (image.endswith(".dcm")):
        all_testNames.append(os.path.join(testFolderPath, image))

random.shuffle(all_filenames)

test_frac = 0.0
num_test = int(len(all_filenames) * test_frac)
num_train = len(all_filenames) - num_test
train_datadict = [{"im": fname} for fname in all_filenames[:num_train]]
test_datadict = [{"im": fname} for fname in all_testNames[:len(all_testNames)]]
print(all_filenames)
print(f"total number of images: {len(all_filenames)}")
print(f"number of images for training: {len(train_datadict)}")
print(f"number of images for testing: {len(test_datadict)}")

train_transforms = Compose(
    [
        LoadImageD(keys=["im"]),
        AddChannelD(keys=["im"]),
        ScaleIntensityD(keys=["im"]),
        RandRotateD(keys=["im"], range_x=np.pi / 12, prob=0.5, keep_size=True),
        RandFlipD(keys=["im"], spatial_axis=0, prob=0.5),
        RandZoomD(keys=["im"], min_zoom=0.9, max_zoom=1.1, prob=0.5),
        ToTensorD(keys=["im"])
    ]
)

test_transforms = Compose(
    [
        LoadImageD(keys=["im"]),
        AddChannelD(keys=["im"]),
        # ScaleIntensityD(keys=["im"]),
        ToTensorD(keys=["im"])
    ]
)

batch_size = 100
# error if greater than 0, https://github.com/Project-MONAI/MONAI/pull/307
num_workers = 0

train_ds = CacheDataset(train_datadict, train_transforms,
                        num_workers=num_workers)
train_loader = DataLoader(train_ds, batch_size=batch_size,
                          shuffle=True, num_workers=num_workers)
test_ds = CacheDataset(test_datadict, test_transforms, num_workers=num_workers)
test_loader = DataLoader(test_ds, batch_size=batch_size,
                         shuffle=True, num_workers=num_workers)


def get_single_im(ds):
    loader = torch.utils.data.DataLoader(
        ds, batch_size=1, num_workers=0, shuffle=True)
    itera = iter(loader)
    return next(itera)


def train(dict_key_for_training, max_epochs=10, learning_rate=1e-3):
    model = AutoEncoder(
        dimensions=2,
        in_channels=1,
        out_channels=1,
        channels=(4, 8, 16, 32),
        strides=(2, 2, 2, 2),
    ).to(device)
    # print( dict_key_for_training )
    # Create loss fn and optimiser
    loss_function = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), learning_rate)

    epoch_loss_values = []

    t = trange(
        max_epochs,
        desc=f"{dict_key_for_training} -- epoch 0, avg loss: inf", leave=True)
    for epoch in t:
        model.train()
        epoch_loss = 0
        step = 0
        for batch_data in train_loader:
            step += 1
            inputs = batch_data[dict_key_for_training].to(device)
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = loss_function(outputs, batch_data[dict_key_for_training].to(device))
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        epoch_loss /= step
        print('OutOfLoop')
        epoch_loss_values.append(epoch_loss)
        t.set_description(
            f"{dict_key_for_training} -- epoch {epoch + 1}"
            + f", average loss: {epoch_loss:.4f}")
    return model, epoch_loss_values


def test(model, dict_key_for_training, max_epochs=10, learning_rate=1e-3):
    loss_function = torch.nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), learning_rate)

    t = trange(
        max_epochs,
        desc=f"{dict_key_for_training} -- epoch 0, avg loss: inf", leave=True)
    model.train(mode=False)

    for batch_data in test_loader1:
        inputs = batch_data[dict_key_for_training].to(device)
        print(batch_data["im_meta_dict"]["filename_or_obj"])
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = loss_function(outputs, batch_data["im"].to(device))
        loss.backward()
        optimizer.step()
        val = loss.item()
        return val


max_epochs = 50
training_types = ['im']
models = []
epoch_losses = []
for training_type in training_types:
    model, epoch_loss = train(training_type, max_epochs=max_epochs)
    models.append(model)
    epoch_losses.append(epoch_loss)

test_loader1 = DataLoader(test_ds, batch_size=1,
                          shuffle=False, num_workers=num_workers)
test_epoch_losses = []
test_models = []
for training_type in training_types:
    test(models[0], training_type, max_epochs=max_epochs)

plt.figure()
plt.title("Training Epoch Average Loss")
plt.xlabel("epoch")
for y, label in zip(epoch_losses, training_types):
    x = list(range(1, len(y) + 1))
    line, = plt.plot(x, y)
    line.set_label(label)
plt.legend()
