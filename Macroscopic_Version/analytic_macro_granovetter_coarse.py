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
print(f'''Analytic Calculations:

Pollution Threshold: {pt}
Social Threshold: {st}

Vulnerability: {vul}
Farsightedness: {far}
Time Horizon: {th}

Lifetime of the ecological dynamics: {tau}
Step Size: {dt}
Integration Time: {it}
''')

print(f'''
Time,    Pollution, Average Activity\n
{T[0]:.{time_precision}f}, {Y0:.6f}, {X0:.6f}''')




# Case number corresponds to paper work not to the Thesis Document

def case00(X0,Y0,C,D, t):
    '''p^+ = 0, p^- = 0
    '''
    X_t = X0
    Y_t = X0 +(Y0-X0)*np.exp(-t/tau)
    return (X_t,Y_t)

def case10(X0,Y0,C, D,t): 
    '''p^+ = C, p^- = 0
    '''
    X_t = X0*np.exp(-C*t)
    if C == rate:        
        Y_t = X0*rate*t*np.exp(-rate*t)+Y0*np.exp(-rate*t)
        #old Y_t = 1 - X0*t*np.exp(-t) + (Y0-1)*np.exp(-t)
    else:
        Y_t = (X0/(1-C*tau))*np.exp(-C*t)+(Y0-(X0/(1-C*tau)))*np.exp(-rate*t)
        #old Y_t = 1- (X0/(1-D))*np.exp(-D*t) +(X0/(1-D)-1+Y0)*np.exp(-t)
    return (X_t,Y_t)


def case01(X0,Y0,C, D, t):
    '''p^+ = 0, p^- = D
    '''
    X_t = 1 + (X0-1)*np.exp(-D*t)
    if D == rate:
        Y_t = 1 + (X0-1)*t*rate*np.exp(-rate*t) + (Y0-1)*np.exp(-rate*t)
        #old Y_t = (1-X0)*t*np.exp(-t) + Y0
    else:
        Y_t = 1+ ((X0-1)/(1-D*tau))*np.exp(-D*t)+(Y0-1-((X0-1)/(1-D*tau)))*np.exp(-rate*t)
        #old Y_t = ((1-X0)/(1-C))*np.exp(-C*t) + ( ((X0-1)/(1-C)) +Y0)*np.exp(-t)
    return (X_t,Y_t)

def case11(X0,Y0,C,D,t): 
    '''p^+ = C, p^- = D
    '''
    s = C+D
    q = D/s
    X_t = q+(X0-q)*np.exp(-s*t)
    if C+D == rate:
        Y_t  = q +(X0-q)*rate*t*np.exp(-rate*t)+(Y0-q)*np.exp(-rate*t)
        #old Y_t = (1-C)-(X0-C)*t*np.exp(-t)+(Y0-(1-C))*np.exp(-t)
    else:
        Y_t = q +((X0-q)/(1-s*tau))*np.exp(-s*t)+(Y0-q-((X0-q)/(1-s*tau)))*np.exp(-rate*t)
        #old Y_t = (1-C/(C+D))+((X0-C/(C+D))/(C+D-1))*np.exp(-(C+D)*t) + ((C/(C+D)) -1 + (C/(C+D)-X0)/(C+D-1) + Y0)*np.exp(-t)
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
    y_dot = (x-y)/tau
    
    # Get the current the current values for the change rates (C_new = p⁺, D_new = p⁻)
    C_new = vul*(y>=pt)+far*(x<st)*((y+y_dot*th)>=pt) 
    D_new = vul*(y<pt)+far*(x>=st)*((y+y_dot*th)<pt)
    # Compare the new to the old ones
    if (C != C_new) or (D != D_new):
        C = C_new
        D = D_new
        t1 = t
        X0 = x
        Y0 = y
        marker.append(t1)
        #Set the right evaluation function
        if (C==0) and (D==0):
            eval_fct = case00 
        elif (C>0) and (D==0):
            eval_fct = case10 
        elif (C==0) and (D>0):
            eval_fct = case01
        elif (C>0) and (D>0):
            eval_fct = case11
        else:
            raise 'EvalError: No eval_fct was chosen '
 
    if y >1:
        print(C,D,t1)
        print(eval_fct)
        raise 'ValError: Pollution out of range'
           #Model parameters
           

    der_X = np.abs(printed_X[-1]-x)
    der_Y = np.abs(printed_Y[-1]-y)
    if (der_X>=prec) or (der_Y >= prec):
        x_new ,y_new = eval_fct(X0,Y0,C=C,D=D,t = t-t1)
        printed_X.append(x_new)
        printed_Y.append(y_new)
        print(f'{t:.{time_precision}f}, {y_new:.4f}, {x_new:.4f}')
    
print(f'===CalculationEnded===')
