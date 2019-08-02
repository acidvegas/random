PROGRESS='#'
for PERCENT in {1..100}; do
	echo -ne "$PERCENT%\t$PROGRESS\r"
	PROGRESS="$PROGRESS#"
	sleep 0.05
done
echo -e "\n"