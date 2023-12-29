#!/bin/bash

folder=$1
scenario_name=$2
time=$3
iterations=$4
cd $folder/$scenario_name

net_file="$scenario_name.net.xml"

python3 ../search_crossing_edges.py $net_file

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

    # Generate random trips for pedestrians
    # P possible values
    p_values=(0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0 1.1 1.2 1.3 1.4 1.5)
    num_options=${#p_values[@]}
    random_index=$((RANDOM % num_options))
    chosen_p=${p_values[$random_index]}
    /usr/share/sumo/tools/randomTrips.py -n $net_file -e $time --pedestrians --random -p $chosen_p
    duarouter -r trips.trips.xml -n $net_file -o pedestrians.rou.xml

    # Generate netstate file
    sumo -c $scenario_name.sumo.cfg --netstate-dump netstate.xml --collision.action warn --intermodal-collision.action warn --log logfile.txt

    # Store the information to describe the simulation
    grep "Simulation ended at time:" logfile.txt > "Netstate/netfile_$new_number.txt"
    vehicles=$(grep "Inserted:" logfile.txt | head -n 1 | sed 's/^[[:space:]]*//')
    echo "Vehicles: $vehicles" >> "Netstate/netfile_$new_number.txt"
    pedestrians=$(grep "Inserted:" logfile.txt | tail -n 1 | sed 's/^[[:space:]]*//')
    echo "Pedestrians: $pedestrians" >> "Netstate/netfile_$new_number.txt"
    grep "Collisions" logfile.txt | sed 's/^[[:space:]]*//' >> "Netstate/netfile_$new_number.txt"
    grep "Emergency" logfile.txt | sed 's/^[[:space:]]*//' >> "Netstate/netfile_$new_number.txt"

    # TODO analyze netstate.xml file to retrieve information about the timestep when a collision of emergency breaking took place (see logfile.txt)
    # pos=730.25 => x=730, y=25

done

> netstate.xml
> cars.rou.xml
> cars.rou.alt.xml
> pedestrians.rou.xml
> pedestrians.rou.alt.xml
> trips.trips.xml
> logfile.txt

exit 1