#!/bin/sh
python main_with_ncflow.py -c=100 &
python main_with_ncflow.py -c=500 &
python main_with_ncflow.py -c=1000 &
python main_with_ncflow.py -c=2000 &
python main_with_ncflow.py -c=5000 &

# python readData.py -c=100 &
# python readData.py -c=500 &
# python readData.py -c=2000 &
# python readData.py -c=5000 &