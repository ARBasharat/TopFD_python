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
import topfd.util.file_util as util
from topfd.msalign.env_base import EnvBase
   
if __name__ == "__main__":
  console_dir =  os.path.realpath(__file__)
  base_dir = console_dir.split("src")[0]
  print("Generate EnvBase pickle file for genertaing theoretical envelope ...")
  parser = argparse.ArgumentParser(description='Preprocess Envelope Data for Feature Extraction')
  parser.add_argument("-f", "--theoreticalPatternFile", default = os.path.join(base_dir, "base_data/theo_patt.txt"), help="Theroretical Pattern file")
  args = parser.parse_args()

  env_base = EnvBase.init_base(args.theoreticalPatternFile)
  util.save_object(env_base, "theo_patt.pkl")
