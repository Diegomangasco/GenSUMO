from sys import argv
from json import dump
from textwrap import dedent
from collections import defaultdict

if __name__ == '__main__':
    file_number = argv[1]
    vehicles_dict = defaultdict(list[list])
    with open('netstate.xml', 'r') as fr:
        all_lines = fr.readlines()
        # Parse all lines to build the dictionary
        for line in all_lines:
            line = dedent(line).replace('\n', '')
            if line.startswith('<timestep'):
                if line.endswith('/>'):
                    break
                time = float(line.split('time="')[1].split('">')[0])
            elif line.startswith('<lane'):
                lane = line.split('id="')[1].split('">')[0]
            elif line.startswith('<vehicle'):
                items = line.split(' ')
                id = int(items[1].split('="')[1].split('"')[0])
                speed = float(items[3].split('="')[1].split('"')[0])
                vehicles_dict[id].append([time, lane, speed])
    
    # Calculate the acceleration by seeing the previous speed for each vehicle
    for _, value in vehicles_dict.items():
        for i, x in enumerate(value):
            if i > 0:
                x.append(round((x[2] - value[i-1][2])/(x[0] - value[i-1][0]), 2))
            else:
                x.append(0.0)

    # Save the result in a json file
    with open('Netstate/netstate_' + file_number + '.json', 'w') as fw:
        dump(vehicles_dict, fw)

