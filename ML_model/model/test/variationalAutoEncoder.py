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
from monai.networks.nets import VarAutoEncoder
from monai.utils import set_determinism

from monai.transforms import (
    AddChannelD,
    Compose,
    LoadImageD,
    ScaleIntensityD,
    ToTensorD,
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
        all_filenames.append(os.path.join(folderPath, jpgFileName))
        sliceNo = sliceNo + 1

all_testNames = []
# all_testNames = ["\PatientId\1-026.dcm","\PatientId\1-027dcm","\PatientId\1-028.dcm",..."\PatientId\1-040.dcm",]
testFolderPath = r'C:\Users\Julia Scott\Desktop\Varian 2020_2021\Prashul\jpeg\Test3'
test_Images_path = os.listdir(testFolderPath)
for n, image in enumerate(test_Images_path):
    if not (image.endswith(".dcm")):
        all_testNames.append( os.path.join(testFolderPath,image) )


random.shuffle(all_filenames)

rand_images = np.random.choice(all_filenames, 8, replace=False)
plot_ims(rand_images, shape=(2, 4))

#Split into training and testing datasets

test_frac = 0.2
num_ims = len(all_filenames)
num_test = int(num_ims * test_frac)
num_train = num_ims - num_test
train_datadict = [{"im": fname} for fname in all_filenames[:num_train]]
test_datadict = [{"im": fname} for fname in all_filenames[-num_test:]]
# test_datadict = [{"im": fname} for fname in all_testNames[:len( all_testNames ) ] ]

print(f"total number of images: {num_ims}")
print(f"number of images for training: {len(train_datadict)}")
print(f"number of images for testing: {len(test_datadict)}")


batch_size = 16
num_workers = 0

transforms = Compose(
    [
        LoadImageD(keys=["im"]),
        AddChannelD(keys=["im"]),
        ScaleIntensityD(keys=["im"]),
        ToTensorD(keys=["im"]),
    ]
)

train_ds = CacheDataset(train_datadict, transforms, num_workers=num_workers)
train_loader = DataLoader(train_ds, batch_size=batch_size,
                          shuffle=True, num_workers=num_workers)
test_ds = CacheDataset(test_datadict, transforms, num_workers=num_workers)
test_loader = DataLoader(test_ds, batch_size=batch_size,
                         shuffle=True, num_workers=num_workers)

# For our loss we'll want to use a combination of a reconstruction loss (here, BCE) and KLD. By increasing the importance of the KLD loss with beta, we encourage the network to disentangle the latent generative factors.

BCELoss = torch.nn.BCELoss(reduction='sum')


def loss_function(recon_x, x, mu, log_var, beta):
    bce = BCELoss(recon_x, x)
    kld = -0.5 * beta * torch.sum(1 + log_var - mu.pow(2) - log_var.exp())
    return bce + kld


def train(in_shape, max_epochs, latent_size, learning_rate, beta):

    model = VarAutoEncoder(
        dimensions=2,
        in_shape=in_shape,
        out_channels=1,
        latent_size=latent_size,
        channels=(16, 32, 64),
        strides=(1, 2, 2),
    ).to(device)

    # Create optimiser
    optimizer = torch.optim.Adam(model.parameters(), learning_rate)

    avg_train_losses = []
    test_losses = []

    t = trange(
        max_epochs, leave=True,
        desc="epoch 0, average train loss: ?, test loss: ?")
    for epoch in t:
        model.train()
        epoch_loss = 0
        for batch_data in train_loader:
            inputs = batch_data['im'].to(device)
            optimizer.zero_grad()

            recon_batch, mu, log_var, _ = model(inputs)
            loss = loss_function(recon_batch, inputs, mu, log_var, beta)
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item()
        avg_train_losses.append(epoch_loss / len(train_loader.dataset))

        # Test
        model.eval()
        test_loss = 0
        with torch.no_grad():
            for batch_data in test_loader:
                inputs = batch_data['im'].to(device)
                recon, mu, log_var, _ = model(inputs)
                # sum up batch loss
                test_loss += loss_function(recon,
                                           inputs, mu, log_var, beta).item()
        test_losses.append(test_loss / len(test_loader.dataset))

        t.set_description(
            f"epoch {epoch + 1}, average train loss: "
            f"{avg_train_losses[-1]:.4f}, test loss: {test_losses[-1]:.4f}")
    return model, avg_train_losses, test_losses

max_epochs = 50
learning_rate = 1e-4
beta = 100  # KL beta weighting. increase for disentangled VAE
latent_size = 2
# VAE constructor needs image shape
im_shape = transforms(train_datadict[0])['im'].shape
print( im_shape )
model, avg_train_losses, test_losses = train(
    im_shape, max_epochs, latent_size, learning_rate, beta)

plt.figure()
plt.title("Epoch losses")
plt.xlabel("Epoch")
plt.ylabel("Loss")
for y, label in zip([avg_train_losses, test_losses],
                    ['avg train loss', 'test loss']):
    x = list(range(1, len(y) + 1))
    line, = plt.plot(x, y)
    line.set_label(label)

plt.legend()
plt.title("Epoch losses")
plt.xlabel("Epoch")
plt.ylabel("Loss")
for y, label in zip([avg_train_losses, test_losses],
                    ['avg train loss', 'test loss']):
    x = list(range(1, len(y) + 1))
    line, = plt.plot(x, y)
    line.set_label(label)
plt.legend()



for j, loader in enumerate([train_loader, test_loader]):
    for i, batch_data in enumerate(loader):
        inputs = batch_data['im'].to(device)
        o = model.reparameterize(
            *model.encode_forward(inputs)).detach().cpu().numpy()
        if i + j == 0:
            latent_coords = o
        else:
            np.vstack((latent_coords, o))

if latent_size < 4:
    fig = plt.figure()
    if latent_size == 2:
        plt.scatter(latent_coords[:, 0],
                    latent_coords[:, 1], c='r', marker='o')
    elif latent_size == 3:
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(latent_coords[:, 0], latent_coords[:, 1],
                   latent_coords[:, 2], c='r', marker='o')
        ax.set_xlabel('dim 1')
        ax.set_ylabel('dim 2')
        ax.set_zlabel('dim 3')


for j, loader in enumerate([train_loader, test_loader]):
    for i, batch_data in enumerate(loader):
        inputs = batch_data['im'].to(device)
        o = model.reparameterize(
            *model.encode_forward(inputs)).detach().cpu().numpy()
        if i + j == 0:
            latent_coords = o
        else:
            np.vstack((latent_coords, o))

if latent_size < 4:
    fig = plt.figure()
    if latent_size == 2:
        plt.scatter(latent_coords[:, 0],
                    latent_coords[:, 1], c='r', marker='o')
    elif latent_size == 3:
        ax = fig.add_subplot(111, projection='3d')
        ax.scatter(latent_coords[:, 0], latent_coords[:, 1],
                   latent_coords[:, 2], c='r', marker='o')
        ax.set_xlabel('dim 1')
        ax.set_ylabel('dim 2')
        ax.set_zlabel('dim 3')


#
# num_ims = 10
# pl.figure(figsize=(20, 12))
# out = [[[] for _ in range(num_ims)] for _ in range(latent_size - 1)]
# dist = torch.distributions.normal.Normal(torch.tensor(0.), torch.tensor(1.))
# model.eval()
# with torch.no_grad():
#     for z in range(latent_size - 1):
#         for z in range(latent_size - 1):
#             for y, j in enumerate(torch.linspace(0.05, 0.95, num_ims)):
#                 for i in torch.linspace(0.05, 0.95, num_ims):
#                     sample = torch.zeros(1, latent_size).to(device)
#                     sample[0, z] = dist.icdf(j)
#                     sample[0, z + 1] = dist.icdf(i)
#                     o = model.decode_forward(sample)
#                     o = o.detach().cpu().numpy().reshape(im_shape[1:])
#                     out[z][y].append(o)
#
# slices = np.block(out)
#
# %matplotlib inline
# pl.figure(figsize=(20, 12))
# for i in range(slices.shape[0]):
#     pl.imshow(slices[i])
#     pl.title(
#         f'slice through dims {i} and {i+1} (through centre of other dims)')
#     if slices.shape[0] > 1:
#         display.clear_output(wait=True)
#         display.display(pl.gcf())
#         time.sleep(0.1)
