import numpy as np
import argparse

WAYS = 4

argParser = argparse.ArgumentParser()
argParser.add_argument("-t", "--time", type=int, help="Seconds of simulation duration")
argParser.add_argument("-l", "--lambda", nargs="+", help="Average number of vehicles generated each second")
argParser.add_argument("-b", "--balanced", type=str, help="Select the modality, yes for balanced, no for unbalanced")

args = vars(argParser.parse_args())

seconds = args["time"]
balanced = True if args["balanced"] == "yes" else False
routes = ["route1", "route2", "route3", "route4", "route5", "route6", "route7", "route8", "route9", "route10", "route11", "route12"]

if balanced:
    lambda_params = list(args["lambda"])
    assert len(lambda_params) == 1
    number_of_departs = np.array([np.random.poisson(lam=float(lambda_params[0]), size=seconds) for _ in range(WAYS)])
else:
    lambda_params = list(args["lambda"]) + list(args["lambda"])
    assert len(lambda_params) == WAYS
    number_of_departs = np.array([np.random.poisson(lam=float(lambda_params[i]), size=seconds) for i in range(WAYS)])

# "<vType accel='2.6' decel='5.0' id='CarA' maxSpeed='14.0' minGap='1.0' sigma='0.5' speedfactor='norm(2,2)' jmIgnoreKeepClearTime='0.1' jmIgnoreJunctionFoeProb='1.0' jmIgnoreFoeProb='0.4'/>" "\n"
with open("cars.rou.xml", "w") as fp:
    fp.writelines(
        "<routes>" + "\n" +
        "<vType accel='6.0' decel='5.0' id='CarA' maxSpeed='14.0' minGap='2.5' sigma='0.5' jmIgnoreFoeProb='0.6'/>" "\n" +
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

    for i in range(seconds):
        departs = number_of_departs[:, i]
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

                fp.writelines(f"<vehicle depart='{i+1}' id='{veh_id}' route='{route}' type='CarA'/>" + "\n")
                veh_id += 1
    fp.writelines("</routes>")

print(f"Total vehicles generated: {veh_id-1}")
print(vehicles)