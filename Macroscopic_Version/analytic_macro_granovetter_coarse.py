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

upt = float(args[1]) # upper pollution threshold
lpt = float(args[2]) # lower pollution threshold
ust = float(args[3]) # upper social    threshold
lst = float(args[4]) # lower social    threshold

vul = float(args[5]) # vulnerability
far = float(args[6]) # farsightedness
th  = float(args[7]) # time horizon

dt  = float(args[8]) # step size
it  = float(args[9]) # integration time (in absolute units)

X0  = float(args[10]) # inital average activity
Y0  = float(args[11]) # inital pollution

if vul == 1:
    print('Error: Vulnerability can not be one.\nCalculation will be exited.')
    exit()
if far == 1:
    print('Error: Farsightedness can not be one.\nCalculation will be exited.')
    exit()
if vul+far == 1:
    print('Error: Vulnerability+Farsightedness can not be one.\nCalculation will be exited.')
    exit()


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
Y_dot = [1-X0-Y0]
marker = [0] #  Set of switching times
eval_fct = None


# Write out the settings and the first line
print(f'''Analytic Calculations:

Upper Pollution Threshold: {upt}
Lower Pollution Threshold: {lpt}
Upper Social Threshold: {ust}
Lower Social Threshold: {lst}

Vulnerability: {vul}
Farsightedness: {far}
Time Horizon: {th}

Step Size: {dt}
Integration Time: {it}
''')

print(f'''
Time,    Pollution, Average Activity\n
{T[0]:.{time_precision}f}, {Y0:.6f}, {X0:.6f}''')




# Case number corresponds to paper work not to the Thesis Document
def case1(X0,Y0,C, D,t): 
    '''p^+ = 0, p^- = D
    '''
    if D == 1:
        X_t = X0*np.exp(-t)
        Y_t = 1 - X0*t*np.exp(-t) + (Y0-1)*np.exp(-t)
    else:
        X_t = X0*np.exp(-D*t)
        Y_t = 1- (X0/(1-D))*np.exp(-D*t) +(X0/(1-D)-1+Y0)*np.exp(-t)
    return (X_t,Y_t)

def case2(X0,Y0,C,D, t):
    '''p^+ = 0, p^- = 0
    '''
    X_t = X0
    Y_t = 1-X0 +(X0-1+Y0)*np.exp(-t)
    return (X_t,Y_t)

def case3(X0,Y0,C, D, t):
    '''p^+ = C, p^- = 0
    '''
    if C == 1:
        X_t = 1 + (X0-1)*np.exp(-t)
        Y_t = (1-X0)*t*np.exp(-t) + Y0
    else:
        X_t = 1 + (X0-1)*np.exp(-C*t)
        Y_t = ((1-X0)/(1-C))*np.exp(-C*t) + ( ((X0-1)/(1-C)) +Y0)*np.exp(-t)
    return (X_t,Y_t)

def case6(X0,Y0,C,D,t): 
    '''p^+ = C, p^- = D
    '''
    if C+D == 1:
        X_t = C+(X0-C)*np.exp(-t)
        Y_t = (1-C)-(X0-C)*t*np.exp(-t)+(Y0-(1-C))*np.exp(-t)
    else:
        X_t = C/(C+D)+(X0-C/(C+D))*np.exp(-(C+D)*t)
        Y_t = (1-C/(C+D))+((X0-C/(C+D))/(C+D-1))*np.exp(-(C+D)*t) + ((C/(C+D)) -1 + (C/(C+D)-X0)/(C+D-1) + Y0)*np.exp(-t)
    return (X_t,Y_t)

def give_the_slope(X0,Y0):
    Y_dot = 1-X0-Y0
    return Y_dot

def make_dir(dir_name):
    if not os.path.isdir(dir_name):
        os.mkdir(dir_name)
        
        


x = X0
y = Y0
for t in T[1:]:
    try:
        (x ,y) = eval_fct(X0,Y0,C=C,D=D,t = t-t1)
        X.append(x)
        Y.append(y)
    except:
        pass
    y_dot = 1-x-y
    
    
    # Check in which range the pollution is 
    if y >= upt: # p^+ = alpha + ?
       if (x >= ust) and (y+y_dot*th>= upt):
           C_new = vul+far
           D_new = 0
           if (C != C_new) or (D != D_new):
               
               C = C_new
               D = D_new
               t1 = t
               X0 = x
               Y0 = y
               #print(f't = {t1:.7f}, switching to case 3 p+ = {C_new} and p- = {D_new}')
               marker.append(t1)
               eval_fct = case3
          
       elif  (x < lst) and (y+y_dot*th < lpt):
           C_new = vul
           D_new = far
           if (C != C_new) or (D != D_new):
               C = C_new
               D = D_new
               t1 = t
               X0 = x
               Y0 = y
               marker.append(t1)
               eval_fct = case6
               #print(f't = {t1:.7f}, switching to case 6 p+ = {C_new} and p- = {D_new}')
           
       else:
           C_new = vul
           D_new = 0
           if (C != C_new) or (D != D_new):
               C = C_new
               D = D_new
               t1 = t
               X0 = x
               Y0 = y
               marker.append(t1)
               eval_fct = case3
               #print(f't = {t1:.7f}, switching to case 3 p+ = {C_new} and p- = {D_new}')
           
    elif y< lpt:
        if (x >= ust) and (y+y_dot*th>= upt):
           C_new = far
           D_new = vul
           if (C != C_new) or (D != D_new):
               C = C_new
               D = D_new
               t1 = t
               X0 = x
               Y0 = y
               marker.append(t1)
               eval_fct = case6
               #print(f't = {t1:.7f}, switching to case 6 p+ = {C_new} and p- = {D_new}')
           
        elif  (x < lst) and (y+y_dot*th < lpt):
           C_new = 0
           D_new = vul+far
           if (C != C_new) or (D != D_new):
               C = C_new
               D = D_new
               t1 = t
               X0 = x
               Y0 = y
               marker.append(t1)
               eval_fct = case1
               #print(f't = {t1:.7f}, switching to case 1 p+ = {C_new} and p- = {D_new}')
           
        else:
           C_new = 0
           D_new = vul
           if (C != C_new) or (D != D_new):
               C = C_new
               D = D_new
               t1 = t
               X0 = x
               Y0 = y
               marker.append(t1)
               eval_fct = case1
               #print(f't = {t1:.7f}, switching to case 1 p+ = {C_new} and p- = {D_new}')
     
    else:
        if (x >= ust) and (y+y_dot*th>= upt):
           C_new = far
           D_new = 0
           if (C != C_new) or (D != D_new):
               C = C_new
               D = D_new
               t1 = t
               X0 = x
               Y0 = y
               marker.append(t1)
               eval_fct = case3
               #print(f't = {t1:.7f}, switching to case 3 p+ = {C_new} and p- = {D_new}')
          
        elif  (x < lst) and (y+y_dot*th < lpt):
           C_new = 0
           D_new = far
           if (C != C_new) or (D != D_new):
               C = C_new
               D = D_new
               t1 = t
               X0 = x
               Y0 = y
               marker.append(t1)
               eval_fct = case1
               #print(f't = {t1}, switching to case 1 p+ = {C_new} and p- = {D_new}')
          
        else:
           C_new = 0
           D_new = 0
           if (C != C_new) or (D != D_new):
               C = C_new
               D = D_new
               t1 = t
               X0 = x
               Y0 = y
               marker.append(t1)
               eval_fct = case2
               #print(f't = {t1}, switching to case 2 p+ = {C_new} and p- = {D_new}')
          
           #Model parameters
           
    
    der_X = np.abs(printed_X[-1]-x)
    der_Y = np.abs(printed_Y[-1]-y)
    if (der_X>=prec) or (der_Y >= prec):
        x_new ,y_new = eval_fct(X0,Y0,C=C,D=D,t = t-t1)
        printed_X.append(x_new)
        printed_Y.append(y_new)
        print(f'{t:.{time_precision}f}, {y_new:.4f}, {x_new:.4f}')
    
print(f'===CalculationEnded===')
