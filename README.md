BeetusBot
=========
Source code for BeetusBot

## Installation
Note: $ means you can execute as a user, # means you need to execute as root (sudo)
clone the repository:

	$ git clone https://github.com/Bakkes/BeetusBot.git

make sure you have the required python dependecies with pip

	# pip install praw
	# pip install mysql-python

Now go to "start the bot" to learn how to start it

### Compatibility
The bot was written in Python 2.7. Make sure you have this installed and set as the system default.
If you don't know how to change the system default, type in Google: "python set systemdefault <distro name>".

## Start the bot

### Manually
To start the bot manually go to the directory you cloned BeetusBot in and type:

	$ ./start.sh

if it doesn't work, make sure you have execute permissions on this file.

### Cron
To start the bot as a cron job use

	$ start.sh bot

to start the subscription service use

	$ start.sh subscription

to start them both use

	$ start.sh both

### Log output

The output of the bot is stored in `beetuslog/log-<currentdate>.log`. You can follow the output with:

	$ tail -f beetuslog/log-<currentdate>.log

## TODO
Rewrite everything
