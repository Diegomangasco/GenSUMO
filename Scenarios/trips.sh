#!/bin/bash

folder=$1
time=$2
iterations=$3
cd $folder

net_file="$folder.net.xml"
touch cars.rou.xml
chmod 777 cars.rou.xml

for ((i=1; i<=$iterations; i++))
do
    # Find the last netstate file inside the folder
    last_file=$(ls -1 Netstate/netfile_* 2>/dev/null | sort -V | tail -n 1)
    current_last_number=$(echo $last_file | grep -oP '\d+')
    new_number=$((current_last_number + 1))
    output_file="Netstate/netfile_$new_number.csv"
    chmod 777 $output_file

    # Generate random trips
    /usr/share/sumo/tools/randomTrips.py -n $net_file -e $time
    duarouter -t trips.trips.xml -n $net_file -o cars.rou.xml

    # Generate netstate  and amitran (trajectories) file
    sumo -c $folder.sumo.cfg --netstate-dump netstate.xml --amitran-output amitran.xml
    chmod 777 netstate.xml
    chmod 777 amitran.xml
    python tools/xml/xml2csv.py netstate.xml --output $output_file

    > trips.trips.xml
    > cars.rou.xml
done

exit 1