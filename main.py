"""
This file contains the basic code to download and store all the data for the 5th and 8th class exam from the Punjab Education Commission
Website. This site achieves that by doing the following:

1. It runs through the entire list of possible roll numbers from '00-000-000' to '99-999-999'.
2. After every page load, it checks if a result was returned. If it was, it stores that result into a local dict indexed
by the roll number.
3. After the run is complete, it takes the dict and then processes it into a dataframe.
"""

import os
from collections import namedtuple

from bs4 import BeautifulSoup
from splinter import Browser

RollNo = namedtuple("RollNo", ['roll_no1', 'roll_no2', 'roll_no3'])


def visit(browser, url, rollno, invalid, outdict, outlist):
    """
    This method visits the given site, fills the form, checks if a valid result is generated, adds the valid result 
    and the valid roll number to the valid dict and valid list respectively.
    
    :param browser: 
    :param url: 
    :param rollno: 
    :param invalid: 
    :param outdict: 
    :param outlist: 
    :return: 
    """
    browser.visit(url)
    browser.fill_form(rollno._asdict())
    browser.find_by_name("search").click()
    if browser.is_text_present(invalid):
        pass
    else:
        outlist.push(rollno)
        outdict['-'.join(rollno)] = browser.html
        with open(os.path.join("dumpdir", '-'.join(rollno))) as f:
            f.write(browser.html)


def process_data(results):
    """
    Iterate through the list of results, extract the data and return it in a list of namedtuples.
    :param results: 
    :return: list of namedtuples.
    """

    result_only = {}
    for key, item in results.items():
        soup = BeautifulSoup(item, "lxml")
        soup = soup.find("div", class_="container")
        result_only[key] = soup

    return result_only


def generate_local_dump(validlist, validdict, outfiletemplate):
    """
    Dumps the list of valid roll numbers to the given file.
    
    :param validlist: 
    :param validdict: 
    :param outfiletemplate: 
    :return: 
    """
    with open(outfiletemplate.format("nums"), 'w') as f:
        f.write('\n'.join(validlist))


# with open(outfiletemplate.format("html"), 'w') as f:
#        f.write('\n'.join(validdict.values))

def download_data():
    rn1 = [str(x).zfill(2) for x in range(0, 100)]
    rn2 = [str(x).zfill(3) for x in range(0, 100)]
    rn3 = [str(x).zfill(3) for x in range(0, 100)]

    rnlist = [RollNo(a, b, c) for a in rn1 for b in rn2 for c in rn3]

    url = "http://pec.edu.pk"
    driver = "chrome"
    valid_roll_no = []

    valid_results = {}
    invalid_result = "No Result found"

    browser = Browser(driver)
    for rn in rnlist:
        visit(browser, url, rn, invalid=invalid_result, outlist=valid_roll_no, outdict=valid_results)

    return (valid_roll_no, valid_results)


valid_roll_no_filename = os.path.join("data", "valids.{}.txt")
rns, rndata = download_data()
rnpdata = process_data(rndata)
generate_local_dump(rns, rnpdata, valid_roll_no_filename)
