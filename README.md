# ASVZ Bot - Automatic Enrollment Script


This is a simple ASVZ (Akademischer Sportverband Zürich) enrollment script for people who always miss the enrollment period of classes as cycling, rowing, etc. It is based on Python with Selenium. Currently, it only works with an ETH Zurich login, but it is quite easy to adapt it to other institutions (which I can't try since I don't have access).

Full instructions to set it up for automatic weekly enrollment are given below.

This is an adapted version from @jstiefel. It works with any enrollment time difference, will keep retrying if lesson is already booked out in case place becomes available, and uses config files for easily enrolling for different lessons. It also doesn't require to install the geckodriver.

## Installation

These instructions are for Ubuntu. It was tested on Ubuntu 18.04, Python 3.7.4 and Firefox 81.0

Clone this repository:

```
cd
git clone https://github.com/bartonp2/asvz_bot.git
```

Set up new virtual environment with venv:

```
sudo pip install venv
python3 -m venv ~/asvz_bot_python
source asvz_bot_python/bin/activate
```

Install Selenium and Firefox webdriver:

```
pip install --upgrade pip
pip install selenium
pip install geckodriver-autoinstaller
deactivate
```

## Run

Enter your login credentials in the credentials.ini file. These will be reused for all your registrations

For each lesson you want to register create a config file like the 'config.ini' example. Link to the corresponding "Sportfahrplan", day, time and facility. Your data is safe since it just uses your own webbrowser. But only use it on your private device since credentials are saved in this file as plain text. 

There are two methods to use this script:

1. Run it manually on the day of enrollment
2. Run one or several as cron job on your device (e.g. Laptop, Raspberry Pi, ...) for automatic weekly enrollment

### 1. Run it manually

Run script once for single enrollment at defined time on the day before enrollment start. Don't close the terminal.

```
cd 
source asvz_bot_python/bin/activate
cd asvz_bot
python asvz_bot.py config.ini
```

### 2. Create a cron job

Copy asvz_bot.py for each enrollment you want to make in one week. Then define a cron job for each of these with corresponding time.

```
crontab -e
```

To run enrollment for example at 21:30 each Tuesday, enter:

```
30 21 * * 2 python asvz_bot.py config.ini
# Shell variable for cron
SHELL=/bin/bash
# PATH variable for cron
PATH=/usr/local/bin:/usr/local/sbin:/sbin:/usr/sbin:/bin:/usr/bin:/usr/bin/X11
# 
# m h  dom mon dow   command
30 21 * * 3 /home/<user>/asvz_bot_python/bin/python /home/<user>/asvz_bot/asvz_bot.py > /home/<user>/asvz_bot/asvz.log 2>&1
```

