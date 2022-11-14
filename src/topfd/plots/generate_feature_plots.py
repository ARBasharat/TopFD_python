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

import numpy as np
# import matplotlib
# matplotlib.use('Agg')
from matplotlib import pyplot as plt

def plot_envelope_sets_2d(env_coll, collection_id):
  for i in range(len(env_coll.env_set_list)):
    env_set = env_coll.env_set_list[i]
    data_grid = np.zeros((len(env_set.exp_env_list), len(env_set.seed_env.peak_list)))
    for spId in range(len(env_set.exp_env_list)):
      for peakIdx in range(len(env_set.seed_env.peak_list)):
        peak = env_set.exp_env_list[spId].peak_list[peakIdx] 
        if peak is not None:
          data_grid[spId, peakIdx] = data_grid[spId, peakIdx] + peak.inte
          
    x = [round(i.pos, 4) for i in env_set.seed_env.peak_list]
    y = list(range(env_coll.start_spec_id, env_coll.end_spec_id + 1))

    plt.Figure()
    plt.imshow(data_grid)#, extent=[x[0],x[-1],y[0],y[-1]])
    plt.xticks(range(len(x)), labels=x, rotation = 90)
    plt.yticks(range(len(y)), labels=y)
    plt.title("Envelope Collection: " + str(collection_id) + " and Envelope Set: " + str(i))
    plt.show()
    plt.close()
    
def plot_envelope_sets_2d_c18(env_coll, collection_id):
  for i in range(len(env_coll.env_set_list)):
    env_set = env_coll.env_set_list[i]
    if env_set.seed_env.charge < 18:
      continue
    data_grid = np.zeros((len(env_set.exp_env_list), len(env_set.seed_env.peak_list)))
    for spId in range(len(env_set.exp_env_list)):
      for peakIdx in range(len(env_set.seed_env.peak_list)):
        peak = env_set.exp_env_list[spId].peak_list[peakIdx] 
        if peak is not None:
          data_grid[spId, peakIdx] = data_grid[spId, peakIdx] + peak.inte
          
    x = [round(i.pos, 4) for i in env_set.seed_env.peak_list]
    y = list(range(env_coll.start_spec_id, env_coll.end_spec_id + 1))

    plt.Figure()
    plt.imshow(data_grid)#, extent=[x[0],x[-1],y[0],y[-1]])
    plt.xticks(range(len(x)), labels=x, rotation = 90)
    plt.yticks(range(len(y)), labels=y)
    plt.title("Envelope Collection: " + str(collection_id) + " and Envelope Set: " + str(i) + " --- " + str(env_set.seed_env.charge))
    plt.show()
    plt.close()

def plot_aggregate_envelopes_c18(env_coll, collection_id):
  for i in range(len(env_coll.env_set_list)):
    env_set = env_coll.env_set_list[i]
    if env_set.seed_env.charge < 18:
      continue
    aggregate_inte = [0] * len(env_set.seed_env.peak_list)
    for spId in range(len(env_set.exp_env_list)):
      for peakIdx in range(0, len(aggregate_inte)):
        peak = env_set.exp_env_list[spId].peak_list[peakIdx] 
        if peak is not None:
          aggregate_inte[peakIdx] = aggregate_inte[peakIdx] + peak.inte
    
    theo_peak_intes = [round(p.inte, 4) for p in env_set.seed_env.peak_list]
    normalized_aggregate_inte = [i/max(aggregate_inte) for i in aggregate_inte]
    
    plt.Figure()
    plt.plot(normalized_aggregate_inte, '')
    plt.plot(theo_peak_intes)
    plt.plot(normalized_aggregate_inte, '.')
    plt.title("Envelope Collection: " + str(collection_id) + " and Envelope Set: " + str(i) + " --- " + str(env_set.seed_env.charge))
    plt.legend(['Agg Env', 'Theo Env'])
    plt.show()
    plt.close()

def plot_envelope_sets_3d(env_coll, collection_id):
  for i in range(len(env_coll.env_set_list)):
    env_set = env_coll.env_set_list[i]
    data_grid = np.zeros((len(env_set.exp_env_list), len(env_set.seed_env.peak_list)))
    for spId in range(len(env_set.exp_env_list)):
      for peakIdx in range(len(env_set.seed_env.peak_list)):
        peak = env_set.exp_env_list[spId].peak_list[peakIdx] 
        if peak is not None:
          data_grid[spId, peakIdx] = data_grid[spId, peakIdx] + peak.inte
          
    x = [round(i.pos, 4) for i in env_set.seed_env.peak_list]
    y = list(range(env_coll.start_spec_id, env_coll.end_spec_id + 1))

    X, Y = np.meshgrid(x, y)
    Z = data_grid
    
    plt.Figure()
    ax = plt.axes(projection='3d')
    ax.plot_wireframe(X, Y, Z)
    ax.set_title("Envelope Collection: " + str(collection_id) + " and Envelope Set: " + str(i))
    plt.show()
    plt.close()
    
def plot_aggregate_envelopes(env_coll, collection_id):
  for i in range(len(env_coll.env_set_list)):
    env_set = env_coll.env_set_list[i]
    aggregate_inte = [0] * len(env_set.seed_env.peak_list)
    for spId in range(len(env_set.exp_env_list)):
      for peakIdx in range(0, len(aggregate_inte)):
        peak = env_set.exp_env_list[spId].peak_list[peakIdx] 
        if peak is not None:
          aggregate_inte[peakIdx] = aggregate_inte[peakIdx] + peak.inte
    
    theo_peak_intes = [round(p.inte, 4) for p in env_set.seed_env.peak_list]
    normalized_aggregate_inte = [i/max(aggregate_inte) for i in aggregate_inte]
    
    plt.Figure()
    plt.plot(normalized_aggregate_inte, '')
    plt.plot(theo_peak_intes)
    plt.plot(normalized_aggregate_inte, '.')
    plt.title("Envelope Collection: " + str(collection_id) + " and Envelope Set: " + str(i))
    plt.legend(['Agg Env', 'Theo Env'])
    plt.show()
    plt.close()
    
def plot_base_envelopes(env_coll, collection_id):
  for i in range(len(env_coll.env_set_list)):
    env_set = env_coll.env_set_list[i]
    selected_exp_envelope = [env for env in env_set.exp_env_list if env.spec_id == env_set.seed_env.spec_id]
    experimental_env_intens = [round(p.inte, 4) if p is not None else 0 for p in selected_exp_envelope[0].peak_list]
    normalized_experimental_env_intens = [i/max(experimental_env_intens) for i in experimental_env_intens]
    theo_peak_intes = [round(p.inte, 4) for p in env_set.seed_env.peak_list]
    
    plt.Figure()
    plt.plot(normalized_experimental_env_intens, '')
    plt.plot(theo_peak_intes)
    plt.plot(normalized_experimental_env_intens, '.')
    plt.title("Envelope Collection: " + str(collection_id) + " and Envelope Set: " + str(i))
    plt.legend(['Exp Env', 'Theo Env'])
    plt.show()
    plt.close()
       