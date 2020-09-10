#!/user/bin/env python

"""
Created on: Mar 20, 2019
Author: Julian Stiefel
License: BSD 3-Clause
Description: Script for automatic enrollment in ASVZ classes
"""

############################# Edit this: ######################################

#ETH credentials:
username = 'xxxx'
password = 'xxxx'
day = 'Donnerstag'
facility = 'Sport Center Polyterrasse'
lesson_time = '19:30'
enrollment_time_difference = 22 #how many hours before registration starts
#link to particular sport on ASVZ Sportfahrplan, e.g. cycling class:
sportfahrplan_particular = 'https://asvz.ch/426-sportfahrplan?f[0]=sport:45645'

###############################################################################

import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys



#run enrollment script:
i = 0 #count
success = False

print("Started waiting")

waiting_fct()

#if there is an exception (no registration possible), enrollment is tried again in total 5 times and then stopped to avoid a lock-out
while not success:
    try:
        success = asvz_enroll()
        print("Script successfully finished")
    except:
        if i<4:
            i += 1
            print("Enrollment failed. Start try number {}".format(i+1))
            pass
        else:
            raise
        
