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

#!/usr/bin/python3

import pandas as pd
from topfd.comp.multiChargeFeature import MultiChargeFeature

class MultiChargeFeatureList():
  def __init__(self, featureList, featureList_singleCharge):
    self.featureList = featureList
    self.featureList_singleCharge = featureList_singleCharge
  
  @classmethod
  def get_multiCharge_features_evaluation(cls, feature_file):
    ## Called from labelling features
    feature_info = pd.read_csv(feature_file, sep=',')
    featureList = []
    for feature_idx in range(0, len(feature_info)):
      featurePd = feature_info.iloc[feature_idx]
      multiChargeFeature = MultiChargeFeature(int(featurePd["FeatureID"]), int(featurePd["MinScan"]), 
                 int(featurePd["MaxScan"]), int(featurePd["MinCharge"]), int(featurePd["MaxCharge"]), 
                 float(featurePd["MonoMass"]), 
                 #int(featurePd["RepCharge"]), 
                 #float(featurePd["RepMz"]), 
                 -1,
                 0,
                 float(featurePd["Abundance"]), float(featurePd["MinElutionTime"]), float(featurePd["MaxElutionTime"]), 
                 float(featurePd["ApexElutionTime"]), float(featurePd["ElutionLength"]), 
                 #float(featurePd["EnvCNNScore"]), 
                 #float(featurePd["PercentMatchedPeaks"]), 
                 #float(featurePd["IntensityCorrelation"]), 
                 #float(featurePd["Top3Correlation"])
                 0,
                 0,
                 0,
                 0
                 )
      multiChargeFeature.ChargeRange = int(featurePd["MaxCharge"]-featurePd["MinCharge"]+1)
      if "Label" in featurePd:
        multiChargeFeature.Label = int(featurePd["Label"])
      #multiChargeFeature.Score = float(featurePd["Score"])
      multiChargeFeature.Score = 1
      featureList.append(multiChargeFeature)
    featureList.sort(key=lambda x: (x.Score), reverse=True)
    return cls(featureList, None)
  
  def __len__(self):
    return len(self.featureList)
  
  def __getitem__(self, index):
    return self.featureList[index]
  
  def __setitem__(self, index, newvalue):
    self.featureList[index] = newvalue
  
  @staticmethod
  def print_features(featureList, filename):
    for idx in range(0, len(featureList)):
      feature = featureList[idx]
      multiChargeFeature = feature.to_dict()
      df = pd.DataFrame(multiChargeFeature, index=[idx])
      if idx == 0:
        df.to_csv(filename, index = False, header=True)
      else:
        df.to_csv(filename, mode='a', index = False, header=False)
        
