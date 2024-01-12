import re
import xml.etree.ElementTree as ET
import math
import pandas as pd
import argparse

argParser = argparse.ArgumentParser()
argParser.add_argument("-d", "--distance", type=float, help="radius that defines the closest vehicles", default=30.0)


args = vars(argParser.parse_args())
distance = args['distance']

def logflie_getter():
    pattern = r"Vehicle\s+'(\d+)'\s+performs\s+emergency\s+braking\s+with\s+decel\s*=\s*(-?\d+\.\d+)\s*wished\s*=\s*(-?\d+\.\d+)\s*severity\s*=\s*(\d+\.\d+),\s*time\s*=\s*(-?\d+\.\d+)"
    
    helper = {}
    helper['vehicle_id'] = []
    helper['time'] = []
    with open('logfile.txt', 'r') as f: 
        for row in f: 
            if row[0] == 'W':
                # Extract the vehicle ID and time from the example text
                match = re.search(pattern, row)
                if match is not None:
                    helper['vehicle_id'].append(int(match.group(1)))
                    helper['time'].append(float(match.group(5)))


    return helper


def compute_distance(x, y, xx, yy): 
    return float(math.sqrt(pow(x-xx, 2) + pow(y-yy, 2)))


def get_vehicle_coords(timestep, id):
    for element in timestep: 
        if float(element.attrib['id']) == id: 
            return float(element.attrib['x']), float(element.attrib['y']), float(element.attrib['speed']), float(element.attrib['angle']), element.attrib['lane']
                  

def xml_data_retriever(data):
    tree = ET.parse('positions.xml')
    root = tree.getroot()
    data_structure = []
    for timestamp in root:
        for i in range(len(data['time'])):
            if float(timestamp.attrib['time']) == data['time'][i]:
                pos_x, pos_y, speed, angle, lane = get_vehicle_coords(timestamp, data['vehicle_id'][i])
                distance_counter = -1 # not to count twice the braking vehicle
                for element in timestamp:  
                    if element.tag == 'vehicle':
                        x =  float(element.attrib['x'])
                        y = float(element.attrib['y'])
                        dist = compute_distance(pos_x, pos_y,x,y)

                        if dist <distance: 
                            distance_counter += 1
                data_structure.append({'time':float(timestamp.attrib['time']), 'lane':lane,'x':x, 'y':y, 'speed':speed, 
                                       'angle':angle, 'closest':distance_counter})
    return data_structure


if __name__ == '__main__': 
    data = logflie_getter()
    data = xml_data_retriever(data)

    # retrieving data
    df = pd.read_csv('data.csv', index_col=None)
    
    # creating new dataframe
    new_data = pd.DataFrame(data, index=None)
    
    df = pd.concat([df, new_data], ignore_index=True)
    # Save the DataFrame to a CSV file
    df.to_csv("data.csv", index=False)