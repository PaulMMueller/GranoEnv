#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 27 19:26:54 2019

@author: paul
This file is used to execute on GranoEnv simulation.
"""

import sys
import granovetter.granovetter as vetter
import timeit

start = timeit.default_timer()

# sys.stdout = open("GranoEnv_output_example.csv", "w+") # Comment in if you use this file directly to parse the output into "GranoEnv_output_example.csv"





input_parameters = sys.argv


    
pollution_threshold  = float(input_parameters[1])
social_threshold = float(input_parameters[2])

vulnerability = float(input_parameters[3])
farsightness = float(input_parameters[4])
time_horizon = float(input_parameters[5])
tau = float(input_parameters[6])

delta_t = float(input_parameters[7])
integration_time = float(input_parameters[8])

initial_pollution = float(input_parameters[9])
initial_average_inactivity = float(input_parameters[10])


number_of_nodes = int(input_parameters[11])
average_degree = int(input_parameters[12])
 
model = input_parameters[13]
small_worldness_parameter = float(input_parameters[14])

if input_parameters[15] == 'False':
    verbose = False
else:
    verbose = True

TG = vetter.granovetter(
        pollution_threshold = pollution_threshold,
        social_threshold = social_threshold,
        vulnerability =  vulnerability,
        farsightness = farsightness,
        time_horizon = time_horizon, 
        tau = tau, 
        delta_t = delta_t,
        integration_time = integration_time,
        initial_average_inactivity=initial_average_inactivity,
        initial_pollution = initial_pollution, 
        number_of_nodes=number_of_nodes,
        average_degree=average_degree,
        model = model,
        small_worldness_parameter=small_worldness_parameter,
        verbose=verbose)


TG.evolve_in_time()
TG.get_pollution_and_set_end_flag()
stop = timeit.default_timer()
print('Runtime: ', stop - start)
