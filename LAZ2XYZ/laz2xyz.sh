#!/bin/bash

for f in *.laz; do
	echo "$f"
	./laszip -i ./"$f" -o ./"${f%.laz}.las"
	las2txt -i ./"${f%.laz}.las" -o ./"${f%.laz}.txt" --parse xyz
	rm *.las
	cat "${f%.laz}.txt" >> $1.xyz
	rm *.txt
done

#~ echo "compressing to tar.gz archive"
#~ tar -czvf $1.tar.gz $1.extra_fields
