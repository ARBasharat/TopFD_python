
#!/usr/bin/python3

##Copyright (c) 2014 - 2021, The Trustees of Indiana University.
##
##Licensed under the Apache License, Version 2.0 (the "License");
##you may not use this file except in compliance with the License.
##You may obtain a copy of the License at
##
##    http://www.apache.org/licenses/LICENSE-2.0
##
##Unless required by applicable law or agreed to in writing, software
##distributed under the License is distributed on an "AS IS" BASIS,
##WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
##See the License for the specific language governing permissions and
##limitations under the License.

import argparse
import tensorflow as tf
import numpy as np
import os
from sklearn.model_selection import train_test_split
from read_model_features import get_features

def get_training_data_all(features_list):
  X = []
  Y = []
  for i in range(0, len(features_list)):
    if features_list[i].Label == 3:
      X.append([features_list[i].EnvcnnScore, features_list[i].rt_range, features_list[i].charge_range, features_list[i].EvenOddPeakRatios, features_list[i].IntensityCorrelation,
            features_list[i].PercentConsecPeaks, features_list[i].PercentMatchedPeaks, features_list[i].Top3Correlation, features_list[i].MaximaNumber, features_list[i].Abundance])
      Y.append(1)
    if features_list[i].Label == 1:
      X.append([features_list[i].EnvcnnScore, features_list[i].rt_range, features_list[i].charge_range, features_list[i].EvenOddPeakRatios, features_list[i].IntensityCorrelation,
            features_list[i].PercentConsecPeaks, features_list[i].PercentMatchedPeaks, features_list[i].Top3Correlation, features_list[i].MaximaNumber, features_list[i].Abundance])
      Y.append(0)
  return X, Y

def test_features_NN_direct(features_list, output_model_fname):
  ## Get data
  X, Y = get_training_data_all(features_list)  
  X_train, X_test, y_train, y_test, = train_test_split(X, Y, test_size=0.33, shuffle=True, random_state=42)
  print("Total Features:", len(Y), "Positive:", sum(Y), "Negative:", len(Y)-sum(Y))
  print("Train Features:", len(y_train), "Positive:", sum(y_train), "Negative:", len(y_train)-sum(y_train))
  print("Test Features:", len(y_test), "Positive:", sum(y_test), "Negative:", len(y_test)-sum(y_test))

  ## Get class weight
  pos = sum(y_train)
  neg = len(y_train)-sum(y_train)
  total = len(y_train)
  weight_for_0 = (1 / neg) * (total / 2.0)
  weight_for_1 = (1 / pos) * (total / 2.0)
  class_weight  = {1:weight_for_1, 0:weight_for_0}
  print("Test Features:", class_weight )
  
  ## Prepare data
  tf.random.set_seed(42)
  train_data = np.array([(xx[0], xx[1]/40.0, xx[2]/30.0, xx[4], xx[5], xx[6], xx[7], 1/xx[9]) for xx in X_train])
  test_data = np.array([(xx[0], xx[1]/40.0, xx[2]/30.0, xx[4], xx[5], xx[6], xx[7], 1/xx[9]) for xx in X_test])

  train_labels = np.array(y_train)
  test_labels = np.array(y_test)

  ## define and train model
  early_stopping = tf.keras.callbacks.EarlyStopping(monitor='val_loss', min_delta=0, patience=30, verbose=1, mode='min')
  checkpoint = tf.keras.callbacks.ModelCheckpoint(output_model_fname, monitor='val_loss', verbose=1, save_best_only=True, mode='min') #Save Model Checkpoint
  model = tf.keras.models.Sequential([
  tf.keras.layers.Input(shape=(8,)),
  tf.keras.layers.Dense(200, kernel_regularizer=tf.keras.regularizers.l1(1e-6)),
  tf.keras.layers.LeakyReLU(alpha=0.05),
  tf.keras.layers.Dense(200, kernel_regularizer=tf.keras.regularizers.l1(1e-6)),
  tf.keras.layers.LeakyReLU(alpha=0.05),
  tf.keras.layers.Dense(200, kernel_regularizer=tf.keras.regularizers.l1(1e-6)),
  tf.keras.layers.LeakyReLU(alpha=0.05),
  tf.keras.layers.Dense(200, kernel_regularizer=tf.keras.regularizers.l1(1e-6)),
  tf.keras.layers.LeakyReLU(alpha=0.05),
  tf.keras.layers.Dense(1, activation='sigmoid')])
  model.compile(loss='binary_crossentropy', optimizer=tf.keras.optimizers.Adam(1E-5), metrics=['accuracy', 'AUC'])
  history = model.fit(train_data, train_labels, verbose=1, epochs=1500, class_weight=class_weight, callbacks=[checkpoint, early_stopping], validation_data=(test_data, test_labels))
  
if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='Extract the proteoform features.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("-F", "--featureFile", default = r"/data/abbash/MS_Feature_Extraction_refactored/src/train/rep_1_multiCharge_features_labeled.csv", help="csv feature file")
  parser.add_argument("-O", "--outputFile", default = "nn_model.h5", help="model name")
  args = parser.parse_args()
  # args.featureFile = r"C:\Users\Abdul\Documents\GitHub\MS_Feature_Extraction_refactored\feature_data_compare_envcnn\SW_480_newFeature_labeled_chargeCorrected\rep_1_multiCharge_features_labeled.csv"

  features_list = get_features(args.featureFile)
  test_features_NN_direct(features_list, args.outputFile)
