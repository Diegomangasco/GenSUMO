import scipy.stats as sc
import numpy as np
import os
import torch.nn as nn
import torch
from collections import Counter
import json
import matplotlib.pyplot as plt
import re

def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)

def convert_to_array(line):
    values = []
    for v in line.values():
        if isinstance(v, dict):
            values.extend(convert_to_array(v))
        else:
            values.append(v)
    return np.array(values)

def labels_getter():
    fp = 'labels'
    labels = []
    helper = []

    for label in sorted_alphanumeric(os.listdir(fp)): 
        with open(fp+'/'+label, 'r') as label:
            labels.append(convert_to_array(json.load(label)))
            helper.append(np.nonzero(labels[-1])[0][0])

    # The folllowing code is needed to project from R18 to Rnum_classes
    # indeed we have no guarantee that all the events that may happen have actually happened. 
    count = Counter(helper)
    num_classes = len(Counter(helper))

    if num_classes != 18: 
        
        converter = {}
        for key in sorted(count.keys()): 
            converter[key] = sorted(count.keys()).index(key)
        
        projected_labels = []
        for id in helper:
            projected_labels.append(nn.functional.one_hot(torch.tensor(converter[id]), num_classes))

        return num_classes, projected_labels, count, converter
    
    else: 
        return num_classes, labels, count, converter

def mapper(index):
    match index: 
        case 0: 
            return 'vehicle-vehicle frontal low'
        case 1: 
            return 'vehicle-vehicle frontal medium'
        case 2: 
            return 'vehicle-vehicle frontal high'
        case 3:
            return 'vehicle-vehicle rear low'
        case 4: 
            return 'vehicle-vehicle rear medium'
        case 5:
            return 'vehicle-vehicle rear high'
        case 6: 
            return 'vehicle-vehicle lateral low'
        case 7: 
            return 'vehicle-vehicle lateral medium'
        case 8:
            return 'vehicle-vehicle lateral high'
        case 9: 
            return 'vehicle-vehicle lateral driver low'
        case 10:
            return 'vehicle-vehicle lateral driver medium'
        case 11: 
            return 'vehicle-vehicle lateral driver high'
        case 12: 
            return 'vehicle-pedestrial low'
        case 13: 
            return 'vehicle-pedestrian medium'
        case 14: 
            return 'vehicle-pedestrian high'
        case 15: 
            return 'braking low'
        case 16: 
            return 'braking medium'
        case 17:
            return 'braking high'

def WilsonConfidenceInterval(alpha=.05, p_hat = .5, n=10): 
    z_a = sc.norm.ppf(1-alpha)

    coeff = 1/(1 + (z_a**2)/n)
    root_coeff = z_a/(2*n)
    root = np.sqrt(4*n*p_hat*(1-p_hat) + z_a**2)
    linear = p_hat + (z_a**2)/(2*n)

    return [coeff*(linear - root_coeff*root), coeff*(linear + root_coeff*root)]


if __name__ =='__main__': 
    class_num, labels, counter, converter = labels_getter()
    to_plot = {}
    for el in counter.keys():
        to_plot[mapper(el)] = counter[el]


    # THIS IS THE WILSON TEST FOR THE SINGLE CLASS
    event = 'vehicle-vehicle lateral driver medium'
    p_r =655/19154

    print(to_plot)

    # here we compute the observed probability
    p_hat = to_plot[event]/sum(to_plot.values())
    print('#'*100)
    print(f'GAN estimated probability: {p_hat}, control: {p_r}')
    print('#'*100)
    print('\n')
    # # effectively, the statistical analysis is given using Wilson's confidence interval. 
    interval_hat = WilsonConfidenceInterval(p_hat=p_hat, n=sum(to_plot.values()))
    interval_r = WilsonConfidenceInterval(p_hat=p_r, n=19154)
    print(f'Control generated: {interval_r}, control: {p_r}')
    print('\n')
    print('#'*100)
    print('\n')
    print('#'*100)
    print('\n')
    print(f'Gan generated: {interval_hat}, p={p_hat}')
    print('\n')
    print('#'*100)

    ##############################################

    # THIS IS THE TEST FOR THE GENERAL CLASS VV vs VP
    # print(sum(list(to_plot.values())[2:]))
    # print(sum(to_plot.values()))
    # p_hat = sum(list(to_plot.values())[2:])/sum(to_plot.values())
    # interval_hat = WilsonConfidenceInterval(p_hat=p_hat, n=sum(to_plot.values()))
    # interval_r = WilsonConfidenceInterval(p_hat=p_r, n=9902)

    # print('#'*90)
    # print('\n')
    # print(f'Gan generated: {interval_r}, p={p_r}')
    # print('\n')
    # print('#'*90)


    # fig = plt.figure()

    # ax = fig.add_subplot()
    # ax.bar(list(to_plot.keys()), to_plot.values())
    # plt.show().keys(), to_plot.values()

    # f_hat = 0
    # print(to_plot)

    # print(f'Fraction of vehicle-vehicle collisions over {100} simulations: {f_hat}')
    # print(f'Fraction of vehicle-vehicle collisions over {100} simulations: {f_hat}')