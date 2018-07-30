#!/bin/bash
i=1
while [ $i -le 33 ]
do
	/bin/python "models.py" $i >> testIndividual.txt
	i=$[$i+1]
done
