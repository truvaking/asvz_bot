#!/home/delt/asvz_bot/asvz_bot/bin/python

"""
Created on: Mar 20, 2019
Author: Julian Stiefel
Edited: Patrick Barton and Matteo Delucchi, October 2020
License: BSD 3-Clause
Description: Script for automatic enrollment in ASVZ classes
"""

import time
import math
import argparse
import configparser
import geckodriver_autoinstaller
from datetime import date, datetime, timedelta
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

day2int = {'Montag': 0,
           'Dienstag': 1,
           'Mittwoch': 2,
           'Donnerstag': 3,
           'Freitag': 4,
           'Samstag': 5,
           'Sonntag': 6}


def waiting_fct():
    def get_lesson_datetime(day, train_time):
        # find next date with that weekday
        nextDate = datetime.today().date()
        while nextDate.weekday() != day2int[day]:
            nextDate += timedelta(days=1)

        # combine with training time for complete date and time object
        lessonTime = datetime.strptime(train_time, '%H:%M').time()
        return datetime.combine(nextDate, lessonTime)

    enrollmentTime = datetime.strptime(
        config['lesson']['enrollment_time'], '%H:%M')
    now = datetime.now()
    enrollmentTime = enrollmentTime.replace(
        year=now.year, month=now.month, day=now.day,)
    if enrollmentTime - now < timedelta(seconds=0):
        enrollmentTime = enrollmentTime.replace(day=enrollmentTime.day + 1)

    # Wait till enrollment opens if script is started before registration time
    delta = enrollmentTime - datetime.today()
    while delta > timedelta(seconds=60):
        print("Time till enrollment opens: " + str(delta))
        if delta < timedelta(minutes=1):
            time.sleep(math.ceil(delta.total_seconds()))
        elif delta < timedelta(minutes=5):
            time.sleep(60)
        elif delta < timedelta(hours=1):
            time.sleep(5*60)
        else:
            time.sleep(60*60)
        delta = enrollmentTime - datetime.today()
    return


def asvz_enroll():
    options = Options()
    options.headless = True
    # open in private mode to avoid different login scenario
    options.add_argument("--private")
    driver = webdriver.Firefox(options=options)

    try:
        driver.get(config['lesson']['sportfahrplan_particular'])
        # wait 20 seconds if not defined differently
        driver.implicitly_wait(20)
        print("Headless Firefox Initialized")
        # find corresponding day div:
        day_ele = driver.find_element_by_xpath(
            "//div[@class='teaser-list-calendar__day'][contains(., '" + config['lesson']['day'] + "')]")
        # search in day div after corresponding location and time
        day_ele.find_element_by_xpath(
            ".//li[@class='btn-hover-parent'][contains(., '" + config['lesson']['facility'] + "')][contains(., '" + config['lesson']['lesson_time'] + "')]").click()

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, "//a[@class='btn btn--block btn--icon relative btn--primary-border' or @class='btn btn--block btn--icon relative btn--primary']"))).click()

        # switch to new window:
        # necessary because tab needs to be open to get window handles
        time.sleep(2)
        tabs = driver.window_handles
        driver.switch_to.window(tabs[1])
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@class='btn btn-default ng-star-inserted' and @title='Login']"))).click()
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@class='btn btn-warning btn-block' and @title='SwitchAai Account Login']"))).click()

        # choose organization:
        organization = driver.find_element_by_xpath(
            "//input[@id='userIdPSelection_iddtext']")
        organization.send_keys('ETH Zurich')
        organization.send_keys(u'\ue006')

        driver.find_element_by_xpath(
            "//input[@id='username']").send_keys(config['creds']['username'])
        driver.find_element_by_xpath(
            "//input[@id='password']").send_keys(config['creds']['password'])
        driver.find_element_by_xpath("//button[@type='submit']").click()

        # wait for button to be clickable for 5 minutes, which is more than enough
        # still needs to be tested what happens if we are on the page before button is enabled
        print("Waiting for enrollment opening")
        elem = WebDriverWait(driver, 300).until(EC.element_to_be_clickable(
            (By.XPATH, "//button[@id='btnRegister' and @class='btn-primary btn enrollmentPlacePadding ng-star-inserted']")))
        time.sleep(2)
        elem.click()
        print("Successfully enrolled. Train hard and have fun!")
    # using non-specific exceptions, since there are different exceptions possible: timeout, element not found because not loaded, etc.
    except:
        driver.quit()
        raise  # re-raise previous exception

    driver.quit()  # close all tabs and window
    return True


# ==== run enrollment script ============================================

# Check if the current version of geckodriver exists
# and if it doesn't exist, download it automatically,
# then add geckodriver to path
geckodriver_autoinstaller.install()

parser = argparse.ArgumentParser(description='ASVZ Bot script')
parser.add_argument('config_file', type=str, help='config file name')
parser.add_argument('--late', default=False, action="store_true",
                    help='use this flag to specify you are late. there will be no waiting function')
args = parser.parse_args()

config = configparser.ConfigParser(allow_no_value=True)
config.read(args.config_file)
config.read('credentials.ini')

if not args.late:
    waiting_fct()

# If lesson is already fully booked keep retrying in case place becomes available again
success = False
while not success:
    try:
        success = asvz_enroll()
    except:
        raise

print("Script finished successfully")
