import numpy as np
import argparse

WAYS = 4

argParser = argparse.ArgumentParser()
argParser.add_argument("-l", "--lambda",default=100, help="Total number of vehicles in the simulation")

args = vars(argParser.parse_args())

routes = ["route1", "route2", "route3", "route4", "route5", "route6", "route7", "route8", "route9", "route10", "route11", "route12"] 

# now we need to divide in 4 parts the number of vehicles
num_vehicles = int(args['lambda'])
departs = []
for j in range(3):
    departs.append(np.random.randint(0, num_vehicles))
    num_vehicles -= departs[j]
departs.append(num_vehicles)


# "<vType accel='2.6' decel='5.0' id='CarA' maxSpeed='14.0' minGap='1.0' sigma='0.5' speedfactor='norm(2,2)' jmIgnoreKeepClearTime='0.1' jmIgnoreJunctionFoeProb='1.0' jmIgnoreFoeProb='0.4'/>" "\n"
with open("cars.rou.xml", "w") as fp:
    fp.writelines(
        "<routes>" + "\n" +
        "<vType accel='7.0' decel='5.0' id='CarA' maxSpeed='18.0' minGap='2.5' sigma='0.5' jmIgnoreFoeProb='0.6'/>" "\n" +
        "<route id='route1' edges='D5 D6' /> <!-- W2E -->" + "\n" +
        "<route id='route2' edges='D7 D8' /> <!-- E2W -->" + "\n" +
        "<route id='route3' edges='D1 D2' /> <!-- S2N -->" + "\n" +
        "<route id='route4' edges='D3 D4' /> <!-- N2S -->" + "\n" +
        "<route id='route5' edges='D5 D4' /> <!-- W2S -->" + "\n" +
        "<route id='route6' edges='D5 D2' /> <!-- W2N -->" + "\n" +
        "<route id='route7' edges='D7 D2' /> <!-- E2N -->" + "\n" +
        "<route id='route8' edges='D7 D4' /> <!-- E2S -->" + "\n" +
        "<route id='route9' edges='D1 D6' /> <!-- S2W -->" + "\n" +
        "<route id='route10' edges='D1 D8' /> <!-- S2E -->" + "\n" +
        "<route id='route11' edges='D3 D8' /> <!-- N2W -->" + "\n" +
        "<route id='route12' edges='D3 D6' /> <!-- N2E -->" + "\n"
    )
    veh_id = 1
    vehicles = {f"Way{t+1}": 0 for t in range(WAYS)}


    for j, dep in enumerate(departs):
        for _ in range(dep):
            if j == 0:
                route = np.random.choice(routes, p=[0.0, 0.0, 0.0, 0.32, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.34, 0.34])
                vehicles[f"Way{j+1}"] += 1
            elif j == 1:
                route = np.random.choice(routes, p=[0.0, 0.32, 0.0, 0.0, 0.0, 0.0, 0.34, 0.34, 0.0, 0.0, 0.0, 0.0])
                vehicles[f"Way{j+1}"] += 1
            elif j == 2:
                route = np.random.choice(routes, p=[0.0, 0.0, 0.32, 0.0, 0.0, 0.0, 0.0, 0.0, 0.34, 0.34, 0.0, 0.0])
                vehicles[f"Way{j+1}"] += 1
            else:
                route = np.random.choice(routes, p=[0.32, 0.0, 0.0, 0.0, 0.34, 0.34, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0])
                vehicles[f"Way{j+1}"] += 1

            fp.writelines(f"<vehicle depart='{0}' id='{veh_id}' route='{route}' type='CarA'/>" + "\n")
            veh_id += 1
    fp.writelines("</routes>")

print(f"Total vehicles generated: {veh_id-1}")
print(vehicles)