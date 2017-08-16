#!/bin/bash
#find the directory of the script
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do # resolve $SOURCE until the file is no longer a symlink
    DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"
    SOURCE="$(readlink "$SOURCE")"
    [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE" # if $SOURCE was a relative symlink, we need to resolve it relative to the path where the symlink file was located
done

#dir contains now the directory of the script
DIR="$( cd -P "$( dirname "$SOURCE" )" && pwd )"

LOG_FILE="$DIR/beetuslog/log-`date +%Y-%m-%d`.log"
DATE=DATE=`date +"%T"`

# if in the current directory the beetus log folder does not exists, make it
[ ! -d $DIR/beetuslog ] && mkdir $DIR/beetuslog && echo "creating log directory"

function logpython(){
	# create the log file (could have used touch)
	echo $DATE >> $LOG_FILE

	# disown the actual script and output the results to a log file
	# ie the current shell is released and another process is forked to execute beetusbot
	python $1 >> $LOG_FILE 2>&1
	echo "--------------" >> $LOG_FILE
}

function runStreamHandler(){
	logpython $DIR/main.py
}
function runCelery(){
	celery multi start 3 -A hfysubs -l info --logfile=$DIR/beetuslog/celery_%n%I.log
}
function runStreamAndCelery(){
	runStreamHandler
	runCelery
}
function inboxhack(){
	logpython $DIR/mainhack.py
}

# read the first argument to see if user already made up his mind
if [ "$1" = "stream" ]
then
	runStreamHandler
	exit 1
elif [ "$1" = "celery" ]
then
	runCelery
	exit 1
elif [ "$1" = "both" ]
then
	runStreamAndCelery
	exit 1
elif [ "$1" = "hack" ]
then
	inboxhack
	exit 1
fi

PS3='How should beetusbot start? '
option_1="Run both the subscription service and the bot"
option_2="Run the stream handler"
option_3="Run the subscription service"
option_4="Quit"
options=("$option_1" "$option_2" "$option_3" "$option_4")
select opt in "${options[@]}"
do
    case $opt in
        $option_1)
			runStreamAndCelery
			break
            ;;
        $option_2)
			runStreamHandler
			break
            ;;
        $option_3)
			runCelery
			break
            ;;
        $option_4)
			inboxhack
			break
            ;;
        $option_5)
            break
            ;;
        *) echo invalid option;;
    esac
done
exit

