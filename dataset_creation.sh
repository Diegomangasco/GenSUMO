#!/bin/bash
# ./dataset_creation.sh /home/diego-pc/Projects/GenerativeSUMO/Scenarios/ 4Ways1Lane 500 1
# to reproduce
# ./dataset_creation.sh /home/sergione/Documents/GenerativeSUMO/Scenarios/ 4Ways1LaneRegulated  simulationdata 75 1

folder=$1
scenario_name=$2
scenario_folder=$3
time=$4
iterations=$5
cd $folder/$scenario_name/$scenario_folder

net_file="$scenario_name.net.xml"

# Only balanced situation between different ways until now
balanced="yes"

for ((i=1; i<=$iterations; i++))
do
    > netstate.xml
    > cars.rou.xml
    > cars.rou.alt.xml
    > pedestrians.rou.xml
    > pedestrians.rou.alt.xml
    > trips.trips.xml
    > logfile.txt
    > positions.xml
    
    # Find the last netstate file inside the folder
    last_file=$(ls -1 Netstate/netfile_* 2>/dev/null | sort -V | tail -n 1)
    current_last_number=$(echo $last_file | grep -oP '\d+')
    new_number=$((current_last_number + 1))

    # Lambda possible values
    lambda_values=(0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0)
    # Get the length of the options array
    num_options=${#lambda_values[@]}
    # Generate a random index
    random_index=$((RANDOM % num_options))
    # Make the random choice
    chosen_lambda=${lambda_values[$random_index]}
    # Generate random trips for vehicles
    python3 random_trips.py -t $time -l $chosen_lambda -b $balanced 
    # python3 fixed_trips.py -l 100

    # Generate random trips for pedestrians
    # P possible values
    p_values=(0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0)
    num_options=${#p_values[@]}
    random_index=$((RANDOM % num_options))
    chosen_p=${p_values[$random_index]}
    /usr/share/sumo/tools/randomTrips.py -n $net_file -e $time --pedestrians --random -p $chosen_p # this is the line to modify to provide the pedestrians
    duarouter -r trips.trips.xml -n $net_file -o pedestrians.rou.xml

    # Generate netstate file, changed to add the positionsoutputs in the positions.xml file
    sumo -c $scenario_name.sumo.cfg --netstate-dump netstate.xml --collision.action warn --collision.check-junctions --fcd-output positions.xml --log logfile.txt --threads 10

    # Store the information to describe the simulation
    grep "Simulation ended at time:" logfile.txt > "Netstate/netfile_$new_number.txt"
    vehicles=$(grep "Inserted:" logfile.txt | head -n 1 | sed 's/^[[:space:]]*//')
    echo "Vehicles: $vehicles" >> "Netstate/netfile_$new_number.txt"
    pedestrians=$(grep "Inserted:" logfile.txt | tail -n 1 | sed 's/^[[:space:]]*//')
    echo "Pedestrians: $pedestrians" >> "Netstate/netfile_$new_number.txt"
    grep "Collisions" logfile.txt | sed 's/^[[:space:]]*//' >> "Netstate/netfile_$new_number.txt"
    grep "Emergency" logfile.txt | sed 's/^[[:space:]]*//' >> "Netstate/netfile_$new_number.txt"

    cd ..
    python3 slicer.py -i $i -n 1
    cd $scenario_folder

    echo "Iteration completed"
done
echo "xml training set crated"

 > netstate.xml
 > cars.rou.xml
 > cars.rou.alt.xml
 > pedestrians.rou.xml
 > pedestrians.rou.alt.xml
 > trips.trips.xml
 > logfile.txt
 > positions.xml

exit 1