import datetime
import torch.nn as nn
import numpy as np
import torch
import os
import random
 

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
 
def rescaler(tensor):
    # min = torch.tensor([[[ -994.8300,  -999.7600,     0.0000,     0.0000]],
    #     [[ -966.2900, -1000.9600,     0.0000,     0.0000]]])
    
    # max = torch.tensor([[[ 999.8700,  994.8300,  359.9900,   17.1500]],
    #     [[1000.9600,  966.3600,  359.9100,    1.8300]]])

    max = torch.tensor([[[ 999.8700,  995.0400,  359.9900,   17.9100]],

        [[1000.9900,  966.3600,  359.9100,    1.8300]]])
    
    min = torch.tensor([[[ -999.6800,  -999.8900,     0.0000,     0.0000]],

        [[ -966.2900, -1001.0000,     0.0000,     0.0000]]])

    tensor[:50, 0] += 4.9915230274e-01#.5004
    tensor[:50, 1] += 5.0041359663e-01#.4995
    tensor[50:, 0] += .4932952821#.488
    tensor[50:, 1] += .5066891909#.507
    
    tensor = torch.cat((tensor[:, [0,1]], torch.zeros((100, 1)), tensor[:, 2].view(100, 1)), 1)
    tensor = torch.reshape(tensor, (-1, 2, 50, 4))
    return ((max-min)*tensor+min).view(100, 4)

class Generator(nn.Module):
    def __init__(self, generator_layer_size, z_size, img_size, class_num):
        super().__init__()

        self.z_size = z_size
        self.img_size = img_size
        input_size = int(img_size/2)

        self.mixing = nn.Linear(self.z_size + class_num, generator_layer_size[0])

        self.final = nn.Linear(img_size, int(2*input_size))

        self.model_v = nn.Sequential(
            nn.Linear(generator_layer_size[0], generator_layer_size[0]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[0], generator_layer_size[1]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[1], generator_layer_size[1]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[1], generator_layer_size[3]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[3], generator_layer_size[3]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[3], generator_layer_size[3]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[3], generator_layer_size[3]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[3], generator_layer_size[3]), 
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[3], input_size)
        )


        self.model_p = nn.Sequential(
            nn.Linear(generator_layer_size[0], generator_layer_size[0]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[0], generator_layer_size[1]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[1], generator_layer_size[1]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[1], generator_layer_size[3]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[3], generator_layer_size[3]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[3], generator_layer_size[3]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[3], generator_layer_size[3]),
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[3], generator_layer_size[3]), 
            nn.LeakyReLU(0.2, inplace=True),
            nn.Linear(generator_layer_size[3], input_size)
        )


        #self.init_weights()

    def forward(self, z, labels):

        # Reshape z
        z = z.view(-1, self.z_size)

        x = torch.cat([z, labels], 1)

        x = nn.functional.leaky_relu(self.mixing(x))

        # Generator out
        out_pedestrian = self.model_p(x)
        out_vehicle = self.model_v(x)

        out = self.final(torch.cat([out_vehicle, out_pedestrian], 1))

        return out.view(-1, 100, 3)#out_pedestrian.view(-1, 2, 50, 4)

def encoder(x, y, ped=False):
    """
        Encodes the position on x and y over the road in a categorical value
    """
    if not ped:
        # LANES
        if 0 < x < 5 and -1010 < y <= -7.20: # D1 LANE VEHICLE
            return 'D1', y.item() 
        elif 0 < x < 5 and 7.20 <= y < 1010: # D2 LANE VEHICLE
            return 'D2', y.item()
        elif -5 < x < 0 and 7.20 <= y < 1010: # D3 LANE VEHICLE
            return 'D3', y.item()
        elif -5 < x < 0 and -1010 < y < -7.20: # D4 LANE VEHICLE
            return 'D4', y.item()
        elif -1010 < x < -7.20 and -5 < y < 0: # D5 LANE VEHCILE
            return 'D5', x.item()
        elif 7.20 < x < 1010 and -5 < y < 0: # D6 LANE VEHICLE
            return 'D6', x.item()
        elif -1010 < x < -7.20 and 0 < y < 5: # D7 LANE VEHICLE 5.20
            return 'D8', x.item()
        elif 7.20 < x < 1000 and 0 < y < 5: # D8 LANE VEHICLE
            return 'D7', x.item()
        
        else: 
            return False, False
        
        # CROSSINGS
        # elif -7.20 < x < -5.20 and -5.20 < y < 5.20:
        #     return x, torch.tensor(9)
        # elif 5.20 < x < 7.20 and -5.20 < y < 5.20:
        #     return x, torch.tensor(10)
        # elif -5.20 < x < 5.20 and -7.20 < y < -5.20:
        #     return y, torch.tensor(11)
        # elif -5.20 < x < 5.20 and 5.20 < y < 7.20:
        #     return y, torch.tensor(12)
        # # INTERSECTION
        # elif -5.20 < x < 5.20 and -5.20 < y < 5.20:
        #     return x, torch.tensor(13)
        # else:
        #     return x, y

def generate_pedestrian_rou_alt(folder, data):

    now = datetime.datetime.now()
    date_time_string = now.strftime("%Y-%m-%d %H:%M:%d")

    header = f"""<?xml version="1.0" encoding="UTF-8"?>

<!-- generated on {date_time_string} by Eclipse SUMO duarouter Version 1.12.0
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/duarouterConfiguration.xsd">

    <input>
        <net-file value="4Ways1LaneRegulated.net.xml"/>
        <route-files value="trips.trips.xml"/>
    </input>

    <output>
        <output-file value="pedestrians.rou.xml"/>
        <alternatives-output value="pedestrians.rou.alt.xml"/>
    </output>

</configuration>
-->\n
"""

    routes = {'D1':'D4', 'D2':'D3', 'D3':'D2', 
              'D4':'D1', 'D5':'D8', 'D6':'D7', 
              'D7':'D6', 'D8':'D5'}

    # # Create a file with header + xmlstr
    with open(folder+"/pedestrians.rou.alt.xml", "w", encoding='UTF-8') as out:
        out.write(header)
    
        out.writelines('<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">\n')

        for i in range(50): 
            line, pos = encoder(data[i+50, 0], data[i+50, 1])
            if line != False: 
                out.writelines(f'\t<person id="{i}" depart="0.00" departPos="{abs(pos)}">\n')
                costs = "2000"
                
                out.writelines(f'\t\t<personTrip from="{line}" to="{routes[line]}" walkFactor="0.75" costs="{costs}"/>\n')
                out.writelines(f'\t</person>\n')
    
        out.writelines('</routes>')

def generate_pedestrian_rou(folder, data): 

    now = datetime.datetime.now()
    date_time_string = now.strftime("%Y-%m-%d %H:%M:%d")

    header = f"""<?xml version="1.0" encoding="UTF-8"?>

<!-- generated on {date_time_string} by Eclipse SUMO duarouter Version 1.12.0
<configuration xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/duarouterConfiguration.xsd">

    <input>
        <net-file value="4Ways1LaneRegulated.net.xml"/>
        <route-files value="trips.trips.xml"/>
    </input>

    <output>
        <output-file value="pedestrians.rou.xml"/>
        <alternatives-output value="pedestrians.rou.alt.xml"/>
    </output>

</configuration>
-->\n
"""
    
    routes = {'D1':'D4', 'D2':'D3', 'D3':'D2', 
              'D4':'D1', 'D5':'D8', 'D6':'D7', 
              'D7':'D6', 'D8':'D5'}
    
    # # Create a file with header + xmlstr
    with open(folder+"/pedestrians.rou.xml", "w", encoding='UTF-8') as out:
        out.write(header)
    
        out.writelines('<routes xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="http://sumo.dlr.de/xsd/routes_file.xsd">\n')
        for i in range(50):

            line, pos = encoder(data[i+50, 0], data[i+50, 1])  

            if line != False:           
                route = line + ' ' + str(routes[line])
                out.writelines(f'\t<person id="{i}" depart="0.00" departPos="{abs(pos)}">\n')
                out.writelines(f'\t\t<walk edges="{route}"/>\n')
                out.writelines(f'\t</person>\n')
    
        out.writelines('</routes>')

def generate_car_rou(folder, tensor): 
    with open(folder+"/cars.rou.xml", "w") as fp:
        fp.writelines(
            "<routes>" + "\n" +
            "<vType accel='7.0' decel='5.0' id='CarA' maxSpeed='18.0' minGap='2.5' sigma='0.5' jmIgnoreJunctionFoeProb='0.6'/>" "\n" +
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

        routes = {'D1':['route3', 'route9', 'route10'],
                  'D3':['route4', 'route11', 'route12'], 
                  'D4':['route4', 'route8', 'route5'],
                  'D5':['route1', 'route5', 'route6'], 
                  'D6':['route1', 'route9', 'route12'],
                  'D7':['route2', 'route7', 'route8']}

        for i in range(50):
            line, pos = encoder(tensor[i, 0], tensor[i, 1])
            if line != False: 
                route = random.sample(routes[line], 1)
                fp.writelines(f"<vehicle depart='{1}' id='{i}' route='{str(route[0])}' departPos='{abs(pos)}' departSpeed='{tensor[i, 3].item()}' departLane='first' type='CarA'/>" + "\n") #{line[1]+'_1'}
        fp.writelines("</routes>")



if __name__ == '__main__': 
    
    if os.getcwd() == '/home/sergione/Documents/GenerativeSUMO': 
        os.chdir('Scenarios/4Ways1LaneRegulated/generatedconfig')
    config_folder = 'generatedconfig'

    if config_folder not in os.listdir(): 
        os.mkdir(config_folder)

    batch_size = 1218#64

    z_size = 10
    input_size = 100*3
    class_num=6

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

    generator_layers = [64, 64, 64, 64]

    generator = Generator(generator_layers, z_size, input_size, class_num).to(device)
    generator.load_state_dict(torch.load('/home/sergione/Documents/GenerativeSUMO/Scenarios/4Ways1LaneRegulated/gan20k/generator'))
    generator.to(device)

    var = torch.sqrt(torch.tensor(10))
    z = torch.randn(1, z_size).to(device)
    fake_labels = torch.LongTensor(np.random.randint(3,6,1)).to(device)
    one_hot_labels = nn.functional.one_hot(fake_labels, class_num)
    # Generate a batch of data
    one_hot_labels[0] = torch.tensor([0, 1, 0, 0, 0, 0])
    generated = generator(z, one_hot_labels).detach()
    data = rescaler(generated[0, :])

    converter={6:0, 9:1, 10:2, 12:3, 13:4, 14:5}
    print(f"generated {mapper(list(converter.keys())[torch.nonzero(one_hot_labels[0]).item()])}")

    generate_pedestrian_rou_alt(config_folder, data)
    generate_pedestrian_rou(config_folder, data)
    generate_car_rou(config_folder, data)