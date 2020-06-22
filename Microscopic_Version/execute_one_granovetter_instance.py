#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon May 27 19:26:54 2019

@author: paul
"""

import sys
import granovetter.granovetter as vetter
import timeit

start = timeit.default_timer()

sys.stdout = open("GranoEnv_output_example.csv", "w+")


# Usable as external file


input_parameters = sys.argv

# Called if paramter number does not fit
if len(input_parameters)== 17:
    number_of_nodes = int(input_parameters[1])
    average_degree = int(input_parameters[2])
    #Thresholds
    upper_social_threshold = float(input_parameters[3])
    lower_social_threshold = float(input_parameters[4])
    
    upper_pollution_threshold  = float(input_parameters[5])
    
    lower_pollution_threshold = float(input_parameters[6])
    
    time_horizon = float(input_parameters[7])
    #Weight of processes
    vulnerability = float(input_parameters[8])
    farsightness = float(input_parameters[9])
    #Time evolution properties
    delta_t = float(input_parameters[10])
    integration_time = int(input_parameters[11])
    #Initial conditions
    initial_pollution = float(input_parameters[12])
    initial_average_activity = float(input_parameters[13])
    #
    model = input_parameters[14]
    small_worldness_parameter = float(input_parameters[15])
    #
    if input_parameters[16] == 'False':
        verbose = False
    else:
        verbose = True

# 
    TG = vetter.granovetter(number_of_nodes=number_of_nodes,average_degree=average_degree,
            upper_social_threshold = upper_social_threshold,
            lower_social_threshold = lower_social_threshold, 
            upper_pollution_threshold = upper_pollution_threshold,
            lower_pollution_threshold = lower_pollution_threshold, 
            time_horizon = time_horizon, 
            vulnerability =  vulnerability, farsightness = farsightness, initial_pollution = initial_pollution, 
            delta_t = delta_t, integration_time = integration_time,model = model,initial_average_activity=initial_average_activity,
            small_worldness_parameter=small_worldness_parameter,verbose=verbose)
    
    
# Use it directly and add paramaters in the following
else: 
    TG = vetter.granovetter(integration_time=10,delta_t =1e-3)
TG.evolve_in_time()
TG.get_pollution_and_set_end_flag()
stop = timeit.default_timer()
print('Runtime: ', stop - start)
