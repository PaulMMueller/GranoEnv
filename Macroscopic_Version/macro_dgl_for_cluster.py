#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 26 15:53:18 2020

@author: paul
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 10:44:03 2019

@author: paul

Piece wise solution of the Macroscopic problem for a fully connected network
p+ = a 1_Y>=Y+ + b 1_X>=gamma+ 1_Y+Y'O>=Y+
p- analog

"""
import numpy as np
import os
import sys

args = sys.argv
print('Start Calc')
prec = 1e-4          # Set a value for the precision. I am to lazy to have it as external parameter.

pt = float(args[1]) # pollution threshold
st = float(args[2]) # social    threshold

vul = float(args[3]) # vulnerability
far = float(args[4]) # farsightedness
th  = float(args[5]) # time horizon

tau = float(args[6]) # Lifetime of the ecological dynamcis
rate = 1/tau # Give the decay/growth rate of the ecological dynamics

dt  = float(args[7]) # step size
it  = float(args[8]) # integration time (in absolute units)

X0  = float(args[9]) # inital average activity
Y0  = float(args[10]) # inital pollution

# pt = 0.6
# st = 0.4
# vul = .1
# far = 10.0
# th = 1000
# tau = 1
# rate = 1/tau
# dt = 1e-3
# it =3
# X0 = 1
# Y0 = .7
w = 1e3

t1 = 0      # Time when we switch from one case to another
C = -1       # unphyiscial
D = -1      # unphyiscal
time_precision = int(np.log10(1/dt))
# Outcome parameters
T = np.arange(0,it,dt)
X = [X0]
Y = [Y0]
printed_X = [X0]
printed_Y = [Y0]
Y_dot = [(X0-Y0)/tau]
marker = [0] #  Set of switching times
eval_fct = None


# Write out the settings and the first line
print(f'''Mean_Field Calculations with Euler:

Pollution Threshold: {pt}
Social Threshold: {st}

Vulnerability: {vul}
Farsightedness: {far}
Time Horizon: {th}

Lifetime of the ecological dynamics: {tau}
Step Size: {dt}
Integration Time: {it}

Initial Average Inactivity: {X0}
Initial Pollution: {Y0}
''')

print(f'''
Time,     Average Inactivity, Pollution,\n
{T[0]:.{time_precision}f}, {X0:.6f}, {Y0:.6f}''')




# Case number corresponds to paper work not to the Thesis Document
def indicator(x,threshold,width):
    return 1/2+np.arctan((x-threshold)*width)/np.pi
    # if x >= threshold:
    #     return 1
    # else:
    #     return 0
    

def give_the_slope(X0,Y0):
    Y_dot = 1-X0-Y0
    return Y_dot

def make_dir(dir_name):
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
        
        

    
last_printed_time_step = 0
x = X0
y = Y0
for t in T[1:]:
    y_dot = (x-y)/tau
    y_new = y+dt*(x-y)
    x_new = x+dt*((1-x)*(vul*(1-indicator(y, pt, w))+far*indicator(x, st, w)*(1-indicator(y+th*y_dot, pt, w)))-
                              x*(vul*indicator(y, pt, w)+far*(1-indicator(x, st, w))*indicator(y+th*y_dot,pt, w)))
 
    
    x = x_new
    y = y_new

    print(f'{t:.{time_precision}f}, {x_new:.6f}, {y_new:.6f}')

    
print(f'===CalculationEnded===')   
