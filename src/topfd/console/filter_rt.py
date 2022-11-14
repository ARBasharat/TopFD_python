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

import sys
import numpy as np
import pandas as pd

import sys

if __name__ == "__main__":
  print("Filter peak by rt")
  input_fname = sys.argv[1]
  start_rt = float(sys.argv[2])
  end_rt = float(sys.argv[3])
  output_fname = sys.argv[4]
  df = pd.read_csv(input_fname, sep = "\t")

  df = df.drop(df[df.retention_time < start_rt].index)
  df = df.drop(df[df.retention_time > end_rt].index)
  min_id = df['spec_id'].min()
  df['spec_id'] = df['spec_id'] - min_id
  df.to_csv(output_fname, sep="\t", index=False)
