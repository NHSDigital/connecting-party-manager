echo $(find changelog -type f -maxdepth 1 | sort -nr | head -1 | sed 's/...$//' | awk -F'changelog/' '{print "release/"$2}')
