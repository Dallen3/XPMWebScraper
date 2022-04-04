from main import main
import configparser
import time
import datetime
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import sys
import scraper
import requests


if __name__ == '__main__':
    timeout = 15 * 60
    config = configparser.ConfigParser()
    config.read("config.ini")
    xeroUserName = config.get("scrapervars", "xeroUserName")
    xeroPassword = config.get("scrapervars", "xeroPassword")
    xeroAuthSeed = config.get("scrapervars", "xeroAuthSeed")
    driver_path = config.get("scrapervars", "driverPath")
    options = Options()
    options.headless = False
    driver = Firefox(options=options, executable_path=driver_path)
    workflowmax_cookie = scraper.get_workflowmax_auth_cookie(xeroUserName, xeroPassword, xeroAuthSeed, driver)
    session = requests.session()
    while True:
        try:
            if scraper.checkAuthenticationCookie(workflowmax_cookie, session) == 200:
                start = time.time()
                main(workflowmax_cookie, session)
                print("----Completed in {0:.0f}s".format(time.time() - start) + "----")
                print(datetime.datetime.now())
                print("Sleep: " + sys.argv[2] + "m")
                time.sleep(int(sys.argv[2]) * 60)
            else:
                driver.close()
                driver = Firefox(options=options, executable_path=driver_path)
                workflowmax_cookie = scraper.get_workflowmax_auth_cookie(xeroUserName, xeroPassword, xeroAuthSeed, driver)
        except Exception as e:
            print(e)

