# GenerativeSUMO

Generative AI to create synthetic SUMO scenarios

## Simple tutorial:

Once the road network has been specified, it is possible to run the simulations and create the dataset running the command: 

./dataset_creation.sh [Project folder] [Parent folder dontaining the folder containing the simulation's data]  [folder conatining the simulation's data] [Time]       [Iterations]

In practice, the bash script dataset_creation.sh Iteratively populates the network via random demand specified by random_trips.py, and then stores in the file 
logfile.txt the happened events with the vehicles implied in the collisions/breaking and their timestamp and ids. 

Each iteration is completed when the python script slicer.py is invoked by dataset:creation.sh. 
Slicer.py classifies each event based on the gravity measure developed in the thesis and creates 2 folders: labels, which contains json coded txt files each specifying the kind of event happened: 

{"vehicle-vehicle": {"frontal": {"low": 0, "medium": 0, "high": 0}, "rear": {"low": 0, "medium": 0, "high": 0}, "lateral": {"low": 0, "medium": 0, "high": 0}, "lateral_driver": {"low": 1, "medium": 0, "high": 0}}, "vehicle-pedestrian": {"low": 0, "medium": 0, "high": 0}, "braking": {"low": 0, "medium": 0, "high": 0}}

and another folder called xml_data_train that stores xml files: screenshot of the network's state of the kind: 

<timestep time="125.90">
        <vehicle id="1" x="-773.30" y="1.60" angle="270.00" type="CarA" speed="14.64" pos="766.10" lane="D8_1" slope="0.00" />
</timestep>


###

Once the execution of the previous command is completed, it is possible to call the 
dataset converter script. It calls the python script train_set_converter.py that based on the given parameters selects the top N vehicles closest to the intersection and saves them into a new folder that now contains npy data. 

###

The training of the network happens via notebook CWGAN.ipynb


### 

Testing the network performance is done via the scenario_tester.sh, that calls python scripts that perform the evaluations. 
THe name of the folder containing the setup files for the simulator must be specified when calling the script. 

# IMPORTANT

# THERE MIGHT BE SOME SYSTEM DEPENDENT PATHS. I HAVE TRIED TO ELIMINATE THEM BUT I MIGHT HAVE BEEN UNSUCCESFULL. 
