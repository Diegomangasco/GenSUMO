# GenerativeSUMO
Generative AI to create synthetic SUMO scenarios

currently added a first dataset creation tool: breaking_analyzer.py that constructs a csv file: 
{'time':float, 'x':float, 'y':float, 'speed':float, 'angle':float, 'lane':str, 'closest':int}, and a clustering
script that performs some exploratory analysis. 

## Dataset

The dataset can be iteratively created and expanded using the provided scripts. In the picture below we can appreciate one of the possible resulting datasets. 
The data is rescaled independently between pedestrians and vehicles. 

![Screenshot from 2024-03-26 18-08-45](https://github.com/Diegomangasco/GenerativeSUMO/assets/103385978/d2025de9-ba66-4155-91ce-5e21a71442f5)

Animation of the current behaviour of the network. 


https://github.com/Diegomangasco/GenerativeSUMO/assets/103385978/caa7e1d7-854e-4ca2-a409-3a8e8391cffb

