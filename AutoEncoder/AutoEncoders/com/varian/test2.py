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
import matplotlib.pyplot as plt

plt.figure()
plt.title("Training Epoch Average Loss")
plt.xlabel("epoch")
epoch_losses = [0.1204,0.0130, 0.0131, 0.0061, 0.0046, 0.0036, 0.0032, 0.0029, 0.0027, 0.0025, 0.0023, 0.0021, 0.0020, 0.0020,
                0.0019, 0.0020, 0.0019, 0.0017, 0.0018, 0.0017, 0.0018, 0.0017, 0.0015, 0.0016, 0.0015, 0.0015, 0.0018,
                0.0014, 0.0017, 0.0014, 0.0013, 0.0013, 0.0013]
print(len(epoch_losses))




epoch_losses_list = [epoch_losses]
training_types = ["images"]
plt.figure()
plt.title("Epoch Average Loss")
plt.xlabel("epoch")
label='Image'
# plt.plot(epoch_losses)
for epoch_loss in epoch_losses:
    line, = plt.plot(epoch_loss, "Image")
    line.set_label(label)
    print( line )

plt.legend()

arr1 = plt.arrow(0,0, 3,1, head_width=0.2, color='r', length_includes_head=True)
arr2 = plt.arrow(0,0, 1,3, head_width=0.2, color='g', length_includes_head=True)
arr3 = plt.arrow(0,0, 4,4, head_width=0.2, color='b', length_includes_head=True)

plt.xlim(0,5)
plt.ylim(0,5)

plt.legend([arr1, arr2, arr3], ['u','v','u+v'])
# 100%|██████████| 3475/3475 [00:13<00:00, 249.57it/s]
# 100%|██████████| 16/16 [00:00<00:00, 501.31it/s]
# im -- epoch 0, avg loss: inf:   0%|          | 0/50 [00:00<?, ?it/s]--->t im -- epoch 0, avg loss: inf:   0%|          | 0/50 [00:00<?, ?it/s]
# im -- epoch 1, average loss: 0.1204:   2%|▏         | 1/50 [03:47<3:05:57, 227.70s/it]
# im -- epoch 2, average loss: 0.0131:   4%|▍         | 2/50 [07:38<3:03:37, 229.53s/it]
#
# im -- epoch 4, average loss: 0.0061:   8%|▊         | 4/50 [15:23<2:57:27, 231.47s/it]
#
# im -- epoch 6, average loss: 0.0046:  12%|█▏        | 6/50 [23:05<2:49:44, 231.47s/it]
#
# im -- epoch 8, average loss: 0.0036:  16%|█▌        | 8/50 [30:54<2:42:41, 232.42s/it]
#
# im -- epoch 10, average loss: 0.0032:  20%|██        | 10/50 [38:35<2:34:26, 231.66s/it]
# im -- epoch 11, average loss: 0.0029:  22%|██▏       | 11/50 [42:28<2:30:49, 232.03s/it]
# im -- epoch 12, average loss: 0.0027:  24%|██▍       | 12/50 [46:20<2:26:55, 231.99s/it]
#
# im -- epoch 14, average loss: 0.0026:  28%|██▊       | 14/50 [54:00<2:18:36, 231.00s/it]
#
# im -- epoch 16, average loss: 0.0025:  32%|███▏      | 16/50 [1:01:54<2:12:18, 233.47s/it]
#
# im -- epoch 18, average loss: 0.0023:  36%|███▌      | 18/50 [1:09:32<2:03:20, 231.26s/it]
#
# im -- epoch 20, average loss: 0.0021:  40%|████      | 20/50 [1:17:15<1:55:52, 231.74s/it]
# im -- epoch 21, average loss: 0.0020:  42%|████▏     | 21/50 [1:21:18<1:53:35, 235.02s/it]
#
# im -- epoch 23, average loss: 0.0020:  46%|████▌     | 23/50 [1:29:35<1:49:00, 242.25s/it]
# im -- epoch 24, average loss: 0.0019:  48%|████▊     | 24/50 [1:33:40<1:45:18, 243.01s/it]
# im -- epoch 25, average loss: 0.0020:  50%|█████     | 25/50 [1:37:34<1:40:06, 240.26s/it]
# im -- epoch 26, average loss: 0.0019:  52%|█████▏    | 26/50 [1:41:13<1:33:34, 233.95s/it]
#
# im -- epoch 28, average loss: 0.0017:  56%|█████▌    | 28/50 [1:48:33<1:23:05, 226.62s/it]
#
# im -- epoch 30, average loss: 0.0018:  60%|██████    | 30/50 [1:55:53<1:14:24, 223.21s/it]
# im -- epoch 31, average loss: 0.0017:  62%|██████▏   | 31/50 [1:59:34<1:10:32, 222.76s/it]
#
# im -- epoch 33, average loss: 0.0018:  66%|██████▌   | 33/50 [2:07:02<1:03:17, 223.37s/it]
# im -- epoch 34, average loss: 0.0017:  68%|██████▊   | 34/50 [2:10:44<59:27, 223.00s/it]
# im -- epoch 35, average loss: 0.0015:  70%|███████   | 35/50 [2:14:25<55:37, 222.52s/it]
# im -- epoch 36, average loss: 0.0016:  72%|███████▏  | 36/50 [2:18:07<51:50, 222.15s/it]
#
# im -- epoch 38, average loss: 0.0015:  76%|███████▌  | 38/50 [2:25:32<44:31, 222.59s/it]
# im -- epoch 39, average loss: 0.0015:  78%|███████▊  | 39/50 [2:29:19<41:02, 223.87s/it]
# im -- epoch 40, average loss: 0.0018:  80%|████████  | 40/50 [2:33:01<37:11, 223.14s/it]
#
# im -- epoch 42, average loss: 0.0014:  84%|████████▍ | 42/50 [2:40:25<29:41, 222.64s/it]
# im -- epoch 43, average loss: 0.0017:  86%|████████▌ | 43/50 [2:44:04<25:52, 221.73s/it]
#
# im -- epoch 45, average loss: 0.0014:  90%|█████████ | 45/50 [2:51:27<18:27, 221.44s/it]
#
# im -- epoch 47, average loss: 0.0013:  94%|█████████▍| 47/50 [2:58:52<11:06, 222.07s/it]
#
# im -- epoch 49, average loss: 0.0013:  98%|█████████▊| 49/50 [3:06:16<03:42, 222.23s/it]
# im -- epoch 50, average loss: 0.0013: 100%|██████████| 50/50 [3:10:01<00:00, 228.03s/it]
