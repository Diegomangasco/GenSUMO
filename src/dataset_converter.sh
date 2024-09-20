#!/bin/sh
echo "converting trainng set to numpy..."

python3 train_set_converter.py -n 1 -d 100 -v 50

echo "training set crated!"
exit 1