#!/bin/bash

folder=$1
scenario_name=$2
time=$3
iterations=$4
cd $folder/$scenario_name

net_file="$scenario_name.net.xml"
touch cars.rou.xml
chmod 777 cars.rou.xml

for ((i=1; i<=$iterations; i++))
do
    # Find the last netstate file inside the folder
    last_file=$(ls -1 Netstate/netfile_* 2>/dev/null | sort -V | tail -n 1)
    current_last_number=$(echo $last_file | grep -oP '\d+')
    new_number=$((current_last_number + 1))
    
    # Generate random trips
    /usr/share/sumo/tools/randomTrips.py -n $net_file -e $time
    duarouter -t trips.trips.xml -n $net_file -o cars.rou.xml

    # Generate netstate file
    sumo -c $scenario_name.sumo.cfg --netstate-dump netstate.xml
    chmod 777 netstate.xml

    # Generate the dataset
    python3 ../dataset_creation.py $new_number

    > trips.trips.xml
    > cars.rou.xml
done

exit 1