import time
import pyotp
import requests

def authenticateXero(xeroUserName, xeroPassword, totp, driver):
    driver.get("http://login.xero.com/identify/user/login")
    emailTestBox = driver.find_element_by_id("xl-form-email")
    passwordTestBox = driver.find_element_by_id("xl-form-password")
    emailTestBox.send_keys(xeroUserName)
    passwordTestBox.send_keys(xeroPassword)
    driver.find_element_by_id("xl-form-submit").click()
    time.sleep(3)
    twoFactorElement = driver.find_element_by_xpath(".//*[@data-automationid='auth-onetimepassword--input']")
    twoFactorElement.send_keys(totp.now())
    driver.find_element_by_xpath(".//*[@data-automationid='auth-submitcodebutton']").click()
    time.sleep(3)


def authenticateXPM(driver,xeroUserName):
    driver.get("http://app.practicemanager.xero.com/")
    time.sleep(3)
    xpmEmail = driver.find_element_by_id("Code")
    xpmEmail.send_keys(xeroUserName)
    driver.find_element_by_id("Login").click()
    time.sleep(10)
    return driver.get_cookie('WorkFlowMax')['value']

def refreshXPM(driver):
    driver.get("http://app.practicemanager.xero.com/")
    time.sleep(2)
    return driver.get_cookie('WorkFlowMax')['value']

def getXPMReport(reportID,WorkFlowMax, report_dict, reportname):
    session = requests.session()
    cookies = {'WorkFlowMax': WorkFlowMax}
    data = '{"design_id":' + reportID + ',"format":"xml"}'
    headers = {'X-AjaxPro-Method': 'Export', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0'}
    start = time.time()
    print("requesting "+reportname)
    response = session.post('https://app.practicemanager.xero.com/ajaxpro/WorkFlowMax.Web.UI.ReportExport,WorkflowMax.App.ashx', cookies=cookies, headers=headers, data=data)
    response = session.get('https://app.practicemanager.xero.com/reports/' + eval(response.text.split(';')[0])['value']['url'], cookies=cookies).text
    request_time = time.time() - start
    print(reportname + " request completed in {0:.0f}s".format(request_time))
    report_dict[reportname] = response[3:]
    session.close()

def checkAuthenticationCookie(WorkFlowMax):
    session = requests.session()
    cookies = {'WorkFlowMax': WorkFlowMax}
    response = session.post('https://app.practicemanager.xero.com/my/overview.aspx', cookies=cookies)
    session.close()
    return response.status_code


def get_workflowmax_auth_cookie(xeroUserName, xeroPassword, xeroAuthSeed, driver):
    totp = pyotp.TOTP(xeroAuthSeed)
    authenticateXero(xeroUserName, xeroPassword, totp, driver)
    auth_cookie = authenticateXPM(driver, xeroUserName)
    return auth_cookie
