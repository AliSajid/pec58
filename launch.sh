#! /bin/bash

for file in $(find /d/experiments/pec58/build/ -maxdepth 1 -mindepth 1 -type d)
do
 num=$(echo $file | tail -c 3)
 echo $num
 docker run --detach -v /d/experiments/pec58/data:/app/data -v /d/experiments/pec58/logs:/app/logs --name worker${num} localhost:5000/range${num}
done
