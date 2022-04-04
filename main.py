import configparser
import multiprocessing
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.options import Options
import requests
import pyotp
import scraper
import scraperdb
import sys


def main(xpm_auth_token, session):
        config = configparser.ConfigParser()
        config.read("config.ini")
        server = config.get("scrapervars", "server")
        dbname = config.get("scrapervars", "dbname")
        dbpw = config.get("scrapervars", "dbpw")
        dbusr = config.get("scrapervars", "dbusr")
        reports = configparser.ConfigParser()
        reports.read(str(sys.argv[1]))
        manager = multiprocessing.Manager()
        report_list = manager.dict()
        processes = list()
        for (reportname, reportnumber) in reports.items("xpmreports"):
            p = multiprocessing.Process(target=scraper.getXPMReport, args=(reportnumber, xpm_auth_token, session, report_list, reportname))
            processes.append(p)
            p.start()
        for proc in processes:
            proc.join()
        for key in report_list:
            connection = scraperdb.getdbconnection(server, dbname, dbusr, dbpw)
            try:
                scraperdb.updateTableFromCSV(connection, key, report_list[key])
            except Exception as e:
                print(e)
                connection.close()
            connection.commit()
            connection.close()
