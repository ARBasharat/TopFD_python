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

import os
import argparse

from topfd.msalign.env_base import EnvBase
import topfd.msalign.msalign_to_env as msalign
import topfd.util.file_util as util

if __name__ == "__main__":
  console_dir =  os.path.realpath(__file__)
  base_dir = console_dir.split("src")[0]
  print("Pre-processing msalign data ...")
  parser = argparse.ArgumentParser(description='Preprocess Envelope Data for Feature Extraction')
  parser.add_argument("-m", "--msalignFile", default="", help="Deconvoluted file containing base peaks")
  parser.add_argument("-f", "--theoreticalPatternFile", default = os.path.join(base_dir, "base_data/theo_patt.pkl"), help="Theroretical Pattern file")
  parser.add_argument("-b", "--percentBound", default = 1.0, type=float, help="Peaks in theoretical who intensity sum is given percentage of total (default: report complete envelope)")
  args = parser.parse_args()

  env_base = util.load_pickle_file_data(args.theoreticalPatternFile)

  envelopes = msalign.get_envelopes_from_msalign(args.msalignFile, env_base, args.percentBound)
  print("Number of base peaks: " + str(len(envelopes)) + "\n")
  
  txt_file = os.path.basename(args.msalignFile).split('.')[0] + "_envs.txt"
  msalign.save_to_txt(envelopes, txt_file)
  
