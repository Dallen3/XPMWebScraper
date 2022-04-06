from main import main
import configparser
import time
import datetime
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import sys
import scraper


if __name__ == '__main__':
    timeout = 15 * 60
    config = configparser.ConfigParser()
    config.read("config.ini")
    xeroUserName = config.get("scrapervars", "xeroUserName")
    xeroPassword = config.get("scrapervars", "xeroPassword")
    xeroAuthSeed = config.get("scrapervars", "xeroAuthSeed")
    driver_path = config.get("scrapervars", "driverPath")
    options = Options()
    options.headless = True
    driver = Firefox(service=Service(GeckoDriverManager().install()), options=options)
    workflowmax_cookie = scraper.get_workflowmax_auth_cookie(xeroUserName, xeroPassword, xeroAuthSeed, driver)
    while True:
        try:
            if scraper.checkAuthenticationCookie(workflowmax_cookie) == 200:
                start = time.time()
                main(workflowmax_cookie)
                print("----Completed in {0:.0f}s".format(time.time() - start) + "----")
                print(datetime.datetime.now())
                print("Sleep: " + sys.argv[2] + "m")
                time.sleep(int(sys.argv[2]) * 60)
            else:
                print("Getting New Auth Token")
                try:
                    driver.close()
                except Exception as e:
                    print(e)
                driver = Firefox(service=Service(GeckoDriverManager().install()), options=options)
                workflowmax_cookie = scraper.get_workflowmax_auth_cookie(xeroUserName, xeroPassword, xeroAuthSeed, driver)
        except Exception as e:
            print(e)

