import re
import xml.etree.ElementTree as ET
import pandas as pd
import argparse
import os
from math import sin, cos, sqrt

argParser = argparse.ArgumentParser()
argParser.add_argument("-i", "--index", type=int)
argParser.add_argument("-d", "--distance", type=float, help="radius that defines the closest vehicles", default=5.0)

args = vars(argParser.parse_args())
distance = args['distance']
index = args['index']
print(distance, index)

def vehicle_collision_gravity(v, angle1, angle2, output): 

    if angle1-angle2 > 0 and 10 <= angle1-angle2: 
        if v <= 6:
            output['lateral'] = 'low'
        elif 6 < v <= 11: 
            output['lateral'] = 'medium'
        else: 
            output['lateral'] = 'high'
    elif angle1-angle2 < 0 and angle1-angle2 < -10: 
        if v <= 5.5:
            output['lateral_driver'] = 'low'
        elif 5.5 < v <= 8: 
            output['lateral_driver'] = 'medium'
        else: 
            output['lateral_driver'] = 'high'
    elif -10 <= angle1 - angle2 <= 10:
        if v <= 7:
            output['rear'] = 'low'
        elif 7 < v <= 14: 
            output['rear'] = 'medium'
        else: 
            output['rear'] = 'high'
    elif 170 <= angle1-angle2 <= 190:
        if v <= 7:
            output['frontal'] = 'low'
        elif 10 < v <= 12.5: 
            output['frontal'] = 'medium'
        else: 
            output['frontal'] = 'high'

def galilean_computer(v1, angle1, v2, angle2, type='pedestrian'):

    output = {}

    if type == 'vehicle': # based on Exploration of vehicle impact speed – injury severity relationships for application in safer road design
        v = 0.5*sqrt((v1)**2 + (v2)**2 - 2*v1*v2+cos(angle1-angle2))
        vehicle_collision_gravity(v, angle1, angle2, output)   
    else: 
        output['module'] = v1
        if output['module'] <= 10.0: 
            output['gravity'] = 'low'
        elif 10.0 < output['module'] <= 15.0: 
            output['gravity'] = 'medium'
        elif 15.0< output['module']: 
            output['gravity'] = 'high'

    return output

def logflie_getter():
    breaking_pattern = r"Vehicle\s+'(\d+)'\s+performs\s+emergency\s+braking\s+with\s+decel\s*=\s*(-?\d+\.\d+)\s*wished\s*=\s*(-?\d+\.\d+)\s*severity\s*=\s*(\d+\.\d+),\s*time\s*=\s*(-?\d+\.\d+)"
    person_collision_pattern = r"Vehicle '(\d+)' collision with person '(\d+)', lane='([^']+)', time=([\d.]+), stage=\S"
    vehicle_collision_pattern = r"Vehicle '(\d+)'; junction collision with vehicle '(\d+)', lane='([^']+)', gap=([-.\d]+), time=([\d.]+) stage=([a-zA-Z]+)"

    vehicles_id = []

    with open('logfile.txt', 'r') as f: 
        t = 0
        time = 0
        for row in f: 
            if row[0] == 'W':
                match = re.search(breaking_pattern, row)
                if match is not None:
                    time = float(match.group(5))
                    vehicles_id.append({'time':time, 'braking':int(match.group(1))})
                match = re.search(person_collision_pattern, row)
                if match is not None: 
                    time = float(match.group(4)) # 4 is time
                    vehicles_id.append({'time':time, 'colliding':int(match.group(1)), 'vehicle_hit':-1, 'person_hit':int(match.group(2))})
                match = re.search(vehicle_collision_pattern, row)
                if match is not None: 
                    time = float(match.group(5)) # 5 is time
                    vehicles_id.append({'time':time, 'colliding':int(match.group(1)), 'vehicle_hit':int(match.group(2)), 'person_hit':-1})
                    
    return vehicles_id

def velocities_getter(data): 
    tree = ET.parse('positions.xml')
    root = tree.getroot()

    for timestamp in root:
        for i in range(len(data)):
            if float(timestamp.attrib['time']) == data[i]['time']:
                for element in timestamp:
                    if 'colliding' in data[i].keys():
                        if element.tag == 'vehicle' and int(element.attrib['id']) == int(data[i]['colliding']): 
                            data[i]['speed_colliding_vehicle'] = element.attrib['speed']
                            data[i]['angle_colliding_vehicle'] = element.attrib['angle']
                        if element.tag == 'vehicle' and int(element.attrib['id']) == int(data[i]['vehicle_hit']):
                            data[i]['speed_vehicle_hit'] = element.attrib['speed']
                            data[i]['angle_vehicle_hit'] = element.attrib['angle']
                        if element.tag == 'person' and int(element.attrib['id']) == int(data[i]['person_hit']): 
                            data[i]['speed_person_hit'] = element.attrib['speed']
                            data[i]['angle_person_hit'] = element.attrib['angle']
                    else: 
                        if element.tag == 'vehicle' and int(element.attrib['id'])== int(data[i]['braking']): 
                            data[i]['x'] = element.attrib['x']
                            data[i]['y'] = element.attrib['y']
                            data[i]['speed_braking_vehicle'] = float(element.attrib['speed'])

    return data

def happened_events(data): 

    data = velocities_getter(vehicles)
    
    list_of_events = {}
    list_of_events['vehicle-vehicle'] = {'frontal':{'low':0, 'medium':0, 'high':0}, 'rear':{'low':0, 'medium':0, 'high':0}, 'lateral':{'low':0, 'medium':0, 'high':0}, 
                                         'lateral_driver':{'low':0, 'medium':0, 'high':0}}
    list_of_events['vehicle-pedestrian'] = {'low':0, 'medium':0, 'high':0}
    list_of_events['braking'] = {'low':0, 'medium':0}
    
    for el in data:

        if 'braking' not in el.keys(): 
            v1 = el['speed_colliding_vehicle']
            angle1 = el['angle_colliding_vehicle']

            if 'speed_person_hit' in el.keys():
                v2 = el['speed_person_hit']
                angle2 = el['angle_person_hit']
                el['gravity'] = galilean_computer(float(v1),float(angle1),float(v2),float(angle2))['gravity']
                list_of_events['vehicle-pedestrian'][el['gravity']] += 1

            elif 'speed_vehicle_hit' in el.keys():
                v2 = el['speed_vehicle_hit']
                angle2 = el['angle_vehicle_hit'] 
                out = galilean_computer(float(v1),float(angle1),float(v2),float(angle2), type='vehicle')
                list_of_events['vehicle-vehicle'][list(out.keys())[0]][out[list(out.keys())[0]]] += 1

        else:
            if el['speed_braking_vehicle'] <= 5: 
                list_of_events['braking']['low'] += 1
            else: 
                list_of_events['braking']['medium'] +=1

    return list_of_events

def xml_data_writer(data, folder_path):
    tree = ET.parse('positions.xml')
    root = tree.getroot()
    for timestamp in root:
        if float(timestamp.attrib['time']) == data[0]['time'] - distance:
            filename = f'simulation:{index}'
            print(filename)
            tree = ET.ElementTree(timestamp)
            tree.write(os.path.join(folder_path, filename))     

def label_writer(data, folder_path='labels'): 
    with open(folder_path, 'a') as fp: 
        fp.write(str(data)+'\n')

if __name__ == '__main__': 
    #Create the folder if it doesn't exist
    folder_path_train = './xml_data_train'
    if not os.path.exists(folder_path_train):
       os.makedirs(folder_path_train)

    vehicles = logflie_getter()
    xml_data_writer(vehicles, folder_path=folder_path_train)

    data = happened_events(vehicles)
    label_writer(data)
