# -*- coding: utf-8 -*-
"""
Created on Thu Mar 11 23:57:44 2021

@author: abbash
"""
import math

def get_msalign_score(score_data_matrices_msalign):
  tolerance = 0.02
  msalign_score = []
  for i in range(0, len(score_data_matrices_msalign)):
    if len(score_data_matrices_msalign[i]['exp_mz']) == 0:
      msalign_score.append(0)
      continue
    msalign_score.append(__calcScrWithSftRatio(tolerance, score_data_matrices_msalign[i]))
  return msalign_score

def __calcMzFactor(id_x, tolerance, theo_env, real_env):
  dist = abs(theo_env[id_x] - real_env[id_x])
  mz_factor = (tolerance - dist) / tolerance
  if (mz_factor < 0):
    mz_factor = 0
  return mz_factor

def __calcIntensityFactor(theo_inte, real_inte):
  if real_inte == 0:
    return 0
  
  ratio = theo_inte / real_inte
  if (ratio > 1.0):
    intensity_factor = 1.0 - 2.0 * (ratio - 1.0)
  else:
    intensity_factor = math.sqrt(ratio)
  
  if intensity_factor < 0:
    intensity_factor = 0
  return intensity_factor

def __calcScrWithSftRatio(tolerance, score_data_matrix_msalign):
  real_env = score_data_matrix_msalign['exp_mz']
  real_env_inte = score_data_matrix_msalign['exp_inte']
  theo_env = score_data_matrix_msalign['theo_mz']
  theo_env_inte = score_data_matrix_msalign['theo_inte']
  s = 0
  for i in range(0, len(real_env)):
    mz_factor = __calcMzFactor(i, tolerance, theo_env, real_env)
    intensity_factor = __calcIntensityFactor(theo_env_inte[i], real_env_inte[i])
    inte_score = math.sqrt(theo_env[i])
    peak_score = mz_factor * intensity_factor * inte_score
    s += peak_score
  return s


      
