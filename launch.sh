#! /bin/bash

read -a nums <<<$(seq 0 625000 10000000)

for ((i=0; i <= 15; i++))
do
    echo "nohup python main.py -s ${nums[i]} -e ${nums[i+1]} &&"
done
