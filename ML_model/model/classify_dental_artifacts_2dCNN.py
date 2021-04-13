import numpy as np
import os
from model.preprocessing import preprocessing
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Conv2D, MaxPool2D, Flatten
from sklearn.model_selection import KFold

acc_per_fold = []
loss_per_fold = []
auc_per_fold = []
os.environ["KERAS_BACKEND"] = "tensorflow"
# 5 folds
kfold = KFold(n_splits=5, shuffle=True)
print('Preprocessing starting')
preprocessingInstance = preprocessing()
xTrain, yTrain, xTest, yTest = preprocessingInstance.getImages()
xTrain, yTrain = preprocessingInstance.getImages()
print('Preprocessing complete')
tf.keras.metrics.AUC(
    num_thresholds=100,
    curve='ROC',
    name=None
)
tf.keras.metrics.Precision(
    thresholds=None, top_k=None, class_id=None, name=None, dtype=None
)

tf.keras.metrics.Recall(
    thresholds=None, top_k=None, class_id=None, name=None, dtype=None
)

fold_no = 1

for train_index, test_index in kfold.split(xTrain):
    model = Sequential()

    # strides is same as subsample
    model.add(Conv2D(32, kernel_size=(3, 3), name='conv1', padding='same', activation='relu',
                     kernel_initializer='he_uniform', input_shape=(512, 512, 1)))
    model.add(MaxPool2D(pool_size=(2, 2), strides=2, padding='valid'))

    model.add(Conv2D(32, kernel_size=(3, 3), name='conv2', padding='same', activation='relu',
                     kernel_initializer='he_uniform'))
    model.add(MaxPool2D(pool_size=(2, 2), strides=2, padding='valid'))

    model.add(Conv2D(32, kernel_size=(3, 3), name='conv3', padding='same', activation='relu',
                     kernel_initializer='he_uniform'))
    model.add(MaxPool2D(pool_size=(2, 2), strides=2, padding='valid'))

    model.add(Conv2D(32, kernel_size=(3, 3), name='conv4', padding='same', activation='relu',
                     kernel_initializer='he_uniform'))
    model.add(MaxPool2D(pool_size=(2, 2), strides=2, padding='valid'))

    model.add(Conv2D(32, kernel_size=(3, 3), name='conv5', padding='same', activation='relu',
                     kernel_initializer='he_uniform'))
    model.add(MaxPool2D(pool_size=(2, 2), strides=2, padding='valid'))

    model.add(Flatten())
    model.add(Dense(64, activation="relu", kernel_initializer="he_uniform"))
    model.add(Dense(3, activation="softmax"))
    # METRICS = [
    #     tf.keras.metrics.sparse_categorical_accuracy(name='accuracy'),
    #     tf.keras.metrics.AUC(name='auc')
    # ]

    model.compile(optimizer='adam', loss='sparse_categorical_crossentropy',
                  metrics=['sparse_categorical_accuracy'])
    model.summary()

    history = model.fit(xTrain[train_index], yTrain[train_index], batch_size=4, verbose=0, epochs=2)

    results = model.evaluate(xTrain[test_index], yTrain[test_index], batch_size=2)

    print(f'Results for fold {fold_no}:')
    print(results)
    print(dict(zip(model.metrics_names, results)))
    acc_per_fold.append(results[1] * 100)
    loss_per_fold.append(results[0])
    # auc_per_fold.append(results[2])
    fold_no = fold_no + 1

# == Provide average scores ==
print('------------------------------------------------------------------------')
print('Score per fold')
for i in range(0, len(acc_per_fold)):
    print('------------------------------------------------------------------------')
    print(f'> Fold {i + 1} - Loss: {loss_per_fold[i]} - Accuracy: {acc_per_fold[i]}% - AUC: {auc_per_fold[i]}')
print('------------------------------------------------------------------------')
print('Average scores for all folds:')
print(f'> Accuracy: {np.mean(acc_per_fold)} (+- {np.std(acc_per_fold)})')
print(f'> Loss: {np.mean(loss_per_fold)}')
print(f'> AUC: {np.mean(auc_per_fold)}')
print('------------------------------------------------------------------------')
