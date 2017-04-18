#! /bin/bash

for file in $(find . -maxdepth 1 -mindepth 1 -type d)
do
 num=$(echo $file | tail -c 3)
 echo $num
 cd $file
 echo "docker build -t pec58/range${num}:1.0 ."
 cd ..
done