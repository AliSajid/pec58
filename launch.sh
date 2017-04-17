#! /bin/bash

read -a nums <<<$(seq 0 1000000 10000000)

for ((i=0; i <= 9; i++))
do
    nohup python main.py -s ${nums[i]} -e ${nums[i+1]} >> logs/data-"${nums[i]}"-"${nums[i+1]}".log &
done
