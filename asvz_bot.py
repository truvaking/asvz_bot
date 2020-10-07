#!/home/<user>/asvz_bot_python/bin/python

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

###############################################################################

import time
import argparse
import configparser
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import geckodriver_autoinstaller


def waiting_fct():
    # if script is started before registration time. Does only work if script is executed on day before event.
    currentTime = datetime.today()
    enrollmentTime = datetime.strptime(config['default']['lesson_time'], '%H:%M')
    enrollmentTime = enrollmentTime.replace(
        hour=enrollmentTime.hour + (24 - config['default'].getint('enrollment_time_difference')))

    while currentTime.hour < enrollmentTime.hour:
        print("Wait for enrollment to open")
        time.sleep(60)
        currentTime = datetime.today()

    if currentTime.hour == enrollmentTime.hour:
        while currentTime.minute < enrollmentTime.minute:
            print("Wait for enrollment to open")
            time.sleep(30)
            currentTime = datetime.today()

    return


def asvz_enroll():
    print('Attempting enroll...')
    options = Options()
    # options.headless = True
    options.add_argument("--private")  # open in private mode to avoid different login scenario
    driver = webdriver.Firefox(options=options)
    print('Got driver')

    try:
        print('Trying to get sportfahrplan')
        driver.get(config['default']['sportfahrplan_particular'])
        driver.implicitly_wait(5)  # wait 20 seconds if not defined differently
        print("Headless Firefox Initialized")
        # find corresponding day div:
        day_ele = driver.find_element_by_xpath(
            "//div[@class='teaser-list-calendar__day'][contains(., '" + config['default']['day'] + "')]")
        # search in day div after corresponding location and time
        if config['default']['description']:
            day_ele.find_element_by_xpath(
                ".//li[@class='btn-hover-parent'][contains(., '" + config['default']['facility'] + "')][contains(., '" +
                config['default']['lesson_time'] + "')][contains(., '" + config['default'][
                    'description'] + "')]").click()
        else:
            day_ele.find_element_by_xpath(
                ".//li[@class='btn-hover-parent'][contains(., '" + config['default']['facility'] + "')][contains(., '" +
                config['default']['lesson_time'] + "')]").click()

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH,
                                                                    "//a[@class='btn btn--block btn--icon relative btn--primary-border' or @class='btn btn--block btn--icon relative btn--primary']"))).click()

        # switch to new window:
        time.sleep(2)  # necessary because tab needs to be open to get window handles
        tabs = driver.window_handles
        driver.switch_to.window(tabs[1])
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@class='btn btn-default ng-star-inserted' and @title='Login']"))).click()
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@class='btn btn-warning btn-block' and @title='SwitchAai Account Login']"))).click()

        # choose organization:
        organization = driver.find_element_by_xpath("//input[@id='userIdPSelection_iddtext']")
        organization.send_keys('ETH Zurich')
        organization.send_keys(u'\ue006')

        driver.find_element_by_xpath("//input[@id='username']").send_keys(username)
        driver.find_element_by_xpath("//input[@id='password']").send_keys(password)
        driver.find_element_by_xpath("//button[@type='submit']").click()

        # wait for button to be clickable for 5 minutes, which is more than enough
        # still needs to be tested what happens if we are on the page before button is enabled
        WebDriverWait(driver, 300).until(EC.element_to_be_clickable((By.XPATH,
                                                                     "//button[@id='btnRegister' and @class='btn-primary btn enrollmentPlacePadding ng-star-inserted']"))).click()
        print("Successfully enrolled. Train hard and have fun!")
    except:  # using non-specific exceptions, since there are different exceptions possible: timeout, element not found because not loaded, etc.
        print('Try failed')
        driver.quit()
        raise  # re-raise previous exception

    driver.quit  # close all tabs and window
    return True


# ==== run enrollment script ============================================

# Check if the current version of geckodriver exists
# and if it doesn't exist, download it automatically,
# then add geckodriver to path
geckodriver_autoinstaller.install()

parser = argparse.ArgumentParser(description='ASVZ Bot script')
parser.add_argument('config_file', type=str, help='config file name')
args = parser.parse_args()

config = configparser.ConfigParser(allow_no_value=True)
config.read(args.config_file)

waiting_fct()

# if there is an exception (no registration possible), enrollment is tried again in total 5 times and then stopped to avoid a lock-out
i = 0  # count
success = False
while not success:
    try:
        success = asvz_enroll()
        print("Script successfully finished")
    except:
        if i < 4:
            i += 1
            print("Enrollment failed. Start try number {}".format(i + 1))
            pass
        else:
            raise
