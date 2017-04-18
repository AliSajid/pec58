#! /bin/bash

for file in $(find . -maxdepth 1 -mindepth 1 -type d)
do
 num=$(echo $file | tail -c 3)
 echo $num
 cd $file
 docker build -t localhost:5000/range${num} .
 docker push localhost:5000/range${num}
 cd ..
done