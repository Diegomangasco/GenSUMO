#!/bin/bash
# to use: ./scenario_tester.sh generatedconfig 50


scenario_folder=$1
iterations=$2

echo "...Initializing simulations..."

for ((i=1; i<=$iterations; i++))
do  
    python3 config_file_generator.py

    cd $scenario_folder
    sumo -c 4Ways1LaneRegulated.sumo.cfg --collision.action warn --collision.check-junctions --log logfile.txt --fcd-output positions.xml

    cd ..
    python3 results_saver.py

    cd $scenario_folder
        > positions.xml
    cd ..

    echo "Iteration $i completed"
done

python3 statistical_tests.py
rm -r labels

