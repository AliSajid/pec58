#! /bin/bash

for file in $(find /d/experiments/pec58/build/ -maxdepth 1 -mindepth 1 -type d)
do
 num=$(echo $file | tail -c 3)
 echo $num
 echo "docker start -d -v /d/experiments/pec58/data:/app/pec58/data -v /d/experiments/pec58/logs:/app/pec58/logs --name worker${num} pec58/image${num}"
done
