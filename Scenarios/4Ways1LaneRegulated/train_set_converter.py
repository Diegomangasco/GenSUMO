import numpy as np
import os
import xml.etree.ElementTree as ET
import argparse
import re

argParser = argparse.ArgumentParser()
argParser.add_argument("-n", "--slices", type=int)

args = vars(argParser.parse_args())
slices = args['slices']


def array_resizer(array, length): 
    a1 = array.shape[0]
    if length - a1 >0: 
        ap = np.zeros((length-a1, 4))
        array = np.vstack([array, ap])
    return array


def max_tensor_len(file):
    tree = ET.parse(file)
    root = tree.getroot()

    hold_v = []
    hold_p = []
    for element in root: 
        
        if element.tag == 'vehicle':
            hold = []
            hold.append(float(element.attrib['x']))
            hold.append(float(element.attrib['y']))
            hold.append(float(element.attrib['angle']))
            hold.append(float(element.attrib['speed']))
            
            hold_v.append(hold)

        elif element.tag == 'person': 
            hold = []
            hold.append(float(element.attrib['x']))
            hold.append(float(element.attrib['y']))
            hold.append(float(element.attrib['angle']))
            hold.append(float(element.attrib['speed']))

            hold_p.append(hold)
    
    return max(len(hold_v), len(hold_p))


def tensor_creator(file, length): 
    tree = ET.parse(file)
    root = tree.getroot()

    hold_v = []
    hold_p = []
    for element in root: 
        
        if element.tag == 'vehicle':
            hold = []
            hold.append(float(element.attrib['x']))
            hold.append(float(element.attrib['y']))
            hold.append(float(element.attrib['angle']))
            hold.append(float(element.attrib['speed']))
            
            hold_v.append(hold)

        elif element.tag == 'person': 
            hold = []
            hold.append(float(element.attrib['x']))
            hold.append(float(element.attrib['y']))
            hold.append(float(element.attrib['angle']))
            hold.append(float(element.attrib['speed']))

            hold_p.append(hold)

    array_v = np.array(hold_v)
    array_p = np.array(hold_p)

    av = array_resizer(array_v, length)
    ap = array_resizer(array_p, length)

    return np.concatenate([av[np.newaxis, ...], ap[np.newaxis, ...]])
        
    
def data_iterator(filepath): 
    
    maxlen = 0
    for file in sorted(os.listdir(filepath)):
        length = max_tensor_len(filepath+'/'+file) 
        if length >= maxlen: 
            maxlen = length

    i = 1
    tensor = np.empty((0, 2, maxlen, 4))
    regex_string = r"simulation:(\d+) slice:(\d+)"
    for file in sorted(os.listdir(filepath)):
        match = re.search(regex_string, file)
        array = tensor_creator(filepath+'/'+file, maxlen)
        tensor = np.vstack([tensor, array[np.newaxis, ...]])
        if i % slices == 0: 
            np.save(os.getcwd()+f'/train/simulation: {match.group(1)}', tensor)
            tensor = np.empty((0, 2, maxlen, 4))
        i += 1
    

if __name__ == '__main__':

    folder_path_train = 'train'
    if not os.path.exists(folder_path_train):
       os.makedirs(folder_path_train)

    filepath = 'xml_data_train'
    data_iterator(filepath)