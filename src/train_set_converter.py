import numpy as np
import os
import xml.etree.ElementTree as ET
import argparse
import re

argParser = argparse.ArgumentParser()
argParser.add_argument("-n", "--slices", type=int)
argParser.add_argument("-d", "--distance", type=float)
argParser.add_argument('-v', "--num_vehic", type=int)

args = vars(argParser.parse_args())
slices = args['slices']


def sorted_alphanumeric(data):
    convert = lambda text: int(text) if text.isdigit() else text.lower()
    alphanum_key = lambda key: [ convert(c) for c in re.split('([0-9]+)', key) ] 
    return sorted(data, key=alphanum_key)


def array_resizer(array, length): 
    a1 = array.shape[0]
    if length - a1 >0: 
        ap = np.zeros((length-a1, 4))
        array = np.vstack([array, ap])
    return array


def tensor_len(file):
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
    
    return len(hold_v), len(hold_p)


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
            hold.append(np.sqrt((hold[0]-500)**2 + (hold[1]+500)**2))
            
            hold_v.append(hold)


        elif element.tag == 'person': 
            hold = []
            hold.append(float(element.attrib['x']))
            hold.append(float(element.attrib['y']))
            hold.append(float(element.attrib['angle']))
            hold.append(float(element.attrib['speed']))
            hold.append(np.sqrt((hold[0]-500)**2 + (hold[1]+500)**2))
            
            hold_p.append(hold)

    array_v = np.array(hold_v)
    array_p = np.array(hold_p)

    av = array_v[array_v[:, 4].argsort()]
    ap = array_p[array_p[:, 4].argsort()]

    av = av[:args['num_vehic'], :4]
    ap = ap[:args['num_vehic'], :4]

    return np.concatenate([av[np.newaxis, ...], ap[np.newaxis, ...]])
        
    
def data_iterator(filepath): 
    
    num_vehic = args['num_vehic']
    chosen_files = []
    for file in sorted_alphanumeric(os.listdir(filepath)):
        length_v, length_p = tensor_len(filepath+'/'+file) 
        if length_v >= num_vehic and length_p >= num_vehic: 
            chosen_files.append(file)
    i = 1
    tensor = np.empty((0, 2, num_vehic, 4))
    regex_string = r"simulation:(\d+) slice:(\d+)"
    for file in sorted_alphanumeric(chosen_files):
        match = re.search(regex_string, file) 
        array = tensor_creator(filepath+'/'+file, num_vehic)
        tensor = np.vstack([tensor, array[np.newaxis, ...]])
        if i % slices == 0: 
            np.save(os.getcwd()+f'/train/simulation:{match.group(1)} slice:{match.group(2)}', tensor)
            tensor = np.empty((0, 2, num_vehic, 4))
        i += 1
    

if __name__ == '__main__':
 
    folder_path_train = 'train'
    if not os.path.exists(folder_path_train):
       os.makedirs(folder_path_train)

    filepath = 'xml_data_train'
    data_iterator(filepath)