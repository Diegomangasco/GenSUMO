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
    output_netstate="Netstate/netfile_$new_number.csv"

    # Find the last amitran file inside the folder
    last_file=$(ls -1 Amitran/amitran_* 2>/dev/null | sort -V | tail -n 1)
    current_last_number=$(echo $last_file | grep -oP '\d+')
    new_number=$((current_last_number + 1))
    output_amitran="Amitran/amitran_$new_number.csv"

    # Generate random trips
    /usr/share/sumo/tools/randomTrips.py -n $net_file -e $time
    duarouter -t trips.trips.xml -n $net_file -o cars.rou.xml

    # Generate netstate  and amitran (trajectories) file
    sumo -c $scenario_name.sumo.cfg --netstate-dump netstate.xml --amitran-output amitran.xml
    chmod 777 netstate.xml
    chmod 777 amitran.xml
    python3 /usr/share/sumo/tools/xml/xml2csv.py netstate.xml --output $output_netstate
    chmod 777 $output_netstate
    python3 /usr/share/sumo/tools/xml/xml2csv.py amitran.xml --output $output_amitran
    chmod 777 $output_amitran

    > trips.trips.xml
    > cars.rou.xml
done

exit 1