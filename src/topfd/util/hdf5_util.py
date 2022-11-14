#!/usr/bin/python3

##Copyright (c) 2014 - 2020, The Trustees of Indiana University.
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
import h5py
import numpy as np
  
from topfd.envelope.seed_envelope import SeedEnvelope
from topfd.env_set.env_set import EnvSet

def create_hdf5_file(env_coll_list, hdf5_filename):
  hdf5_file = h5py.File(hdf5_filename, mode='a') 
  for collection_idx in range(0, len(env_coll_list)): ########
    print("Writing Envelope Collection", collection_idx, "out of", len(env_coll_list))
    env_coll = env_coll_list[collection_idx]
    parent_group = hdf5_file.create_group("Envelope_Collection_" + str(collection_idx))
    _write_seed_envelope(parent_group, env_coll)
    _write_envelope_sets(parent_group, env_coll)
  hdf5_file.close()
  
def _write_seed_envelope(parent_group, env_coll):
  seed_env = env_coll.seed_env
  seed_envelope_group = parent_group.create_group("Seed_Envelope")
  seed_envelope_group['spec_id'] = seed_env.spec_id 
  seed_envelope_group['env_id'] = seed_env.env_id
  seed_envelope_group['pos'] = seed_env.pos
  seed_envelope_group['mass'] = seed_env.mass ## GET VALUES -- seed_envelope_group['mass'][()]
  seed_envelope_group['inte'] = seed_env.inte
  seed_envelope_group['charge'] = seed_env.charge  
  seed_envelope_group['theoretical_envelope_masses'] = [p.pos if p is not None else 0 for p in seed_env.peak_list]
  seed_envelope_group['theoretical_envelope_intes'] = [p.inte if p is not None else 0 for p in seed_env.peak_list]

def _write_envelope_sets(parent_group, env_coll):
    envelope_sets_group = parent_group.create_group("Envelope_Sets")
    x = len(env_coll.seed_env.peak_list)
    y = env_coll.end_spec_id - env_coll.start_spec_id + 1
    for envelope_set_idx in range(0, len(env_coll.env_set_list)):
      print("Writing Envelope Set", envelope_set_idx, "out of", len(env_coll.env_set_list))
      envelope_set = env_coll.env_set_list[envelope_set_idx]
      _write_envelope_set(envelope_sets_group, envelope_set, envelope_set_idx)
      
def _write_envelope_set(envelope_sets_group, envelope_set, envelope_set_idx):
  exp_mz = np.zeros((y, x))
  exp_intensities = np.zeros((y, x))
  for envelope_idx in range(0, len(envelope_set.exp_env_list)):
    envelope = envelope_set.exp_env_list[envelope_idx]
    for peak_idx in range(0, len(envelope.peak_list)):
      peak = envelope.peak_list[peak_idx]
      if peak is not None:
        exp_mz[envelope_idx][peak_idx] = exp_mz[envelope_idx][peak_idx] + peak.pos
        exp_intensities[envelope_idx][peak_idx] = exp_intensities[envelope_idx][peak_idx] + peak.inte
  envelope_set_group = envelope_sets_group.create_group(str(envelope_set_idx))
  envelope_set_group['experiemntal_peak_masses'] = exp_mz
  envelope_set_group['experiemntal_peak_intes'] = exp_intensities
  envelope_set_group['theoretical_envelope_masses'] = [p.pos if p is not None else 0 for p in envelope_set.seed_env.peak_list]
  envelope_set_group['theoretical_envelope_intes'] = [p.inte if p is not None else 0 for p in envelope_set.seed_env.peak_list]

  
def read_dataset(hdf5_filename):
  data = h5py.File(hdf5_filename, 'r')
  
  env_colls = []
  for env_coll_key in data.keys():
    break
    env_collection = data[env_coll_key]
    spec_id = env_collection['Seed_Envelope']['spec_id'][()]
    env_id = env_collection['Seed_Envelope']['env_id'][()]
    pos = env_collection['Seed_Envelope']['pos'][()]
    mass = env_collection['Seed_Envelope']['mass'][()]
    inte = env_collection['Seed_Envelope']['inte'][()]
    charge = env_collection['Seed_Envelope']['charge'][()]
    
    pos_list = env_collection['Seed_Envelope']['theoretical_envelope_masses'][()]
    inte_list = env_collection['Seed_Envelope']['theoretical_envelope_intes'][()]
    seed_env = SeedEnvelope(spec_id, env_id, pos, mass, inte, charge, pos_list, inte_list)
    
    # envelope_sets = []
    # for env_set_keys in env_collection['Envelope_Sets']:
    #   print(env_set_keys)
    #   theo_env_masses = 
    
    # break
  