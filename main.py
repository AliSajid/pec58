"""
This file contains the basic code to download and store all the data for the 5th and 8th class exam from the Punjab Education Commission
Website. This site achieves that by doing the following:

1. It runs through the entire list of possible roll numbers from '00-000-000' to '99-999-999'.
2. After every page load, it checks if a result was returned. If it was, it stores that result into a local sqplite db indexed
by the roll number, otherwise it commits a NULL to it.
3. After the run is complete, it takes the db and processes the data.
"""
import time
from collections import namedtuple
from optparse import OptionParser
from os import path

from pony import orm
from requests import post

parser = OptionParser()

parser.add_option("-s", "--start-num", dest="start", type="int", default=0)
parser.add_option("-e", "--end-num", dest="end", type="int", default=10000000)
(options, args) = parser.parse_args()

# if len(args) != 2:
#    parser.error("incorrect number of arguments")

RollNo = namedtuple("RollNo", ['roll_no1', 'roll_no2', 'roll_no3', "search"])
DBNAME = "data-{:0>8}-{:0>8}.sqlite".format(options.start, options.end)
DIRNAME = "data"

db = orm.Database()
db.bind('sqlite', path.join(DIRNAME, DBNAME), create_db=True)


class Record(db.Entity):
    idx = orm.Required(int)
    rollno1 = orm.Required(str)
    rollno2 = orm.Required(str)
    rollno3 = orm.Required(str)
    html = orm.Required(str)
    error = orm.Required(bool)


db.generate_mapping(create_tables=True)


@orm.db_session
def visit(url, rollno, invalid, idx):
    """
    This method visits the given site, fills the form, checks if a valid result is generated, adds the valid result 
    and the valid roll number to the valid dict and valid list respectively.
    
    :param url: 
    :param rollno: 
    :param invalid: 
    """
    res = post(url, rollno._asdict())
    if res.text.find(invalid) != -1:
        Record(rollno1=rollno[0], rollno2=rollno[1], rollno3=rollno[2], html="NULL", error=True, idx=idx)
    else:
        Record(rollno1=rollno[0], rollno2=rollno[1], rollno3=rollno[2], html=res.text, error=False, idx=idx)


# def process_data(results):
#     """
#     Iterate through the list of results, extract the data and return it in a list of namedtuples.
#     :param results:
#     :return: list of namedtuples.
#     """
#
#     result_only = {}
#     for key, item in results.items():
#         soup = BeautifulSoup(item, "lxml")
#         soup = soup.find("div", class_="container")
#         result_only[key] = soup
#
#     return result_only

def download_data(from_num, to_num):
    rn1 = [str(x).zfill(2) for x in range(0, 100)]
    rn2 = [str(x).zfill(3) for x in range(0, 100)]
    rn3 = [str(x).zfill(3) for x in range(0, 100)]

    rnlist = [RollNo(a, b, c, "") for a in rn1 for b in rn2 for c in rn3]

    URL = "http://pec.edu.pk"
    INVALID_RESULT = "No Result found"

    print("Start Parameter is: {}".format(options.start))
    print("End Parameter is: {}".format(options.end))
    print("Saving data to database {}".format(DBNAME))

    with orm.db_session:
        last_record = orm.max(r.id for r in Record)

        if last_record == to_num:
            print("No new data to download. Exiting...")
            return

        if last_record:
            last_roll_num = RollNo(
                *list(orm.select((r.rollno1, r.rollno2, r.rollno3) for r in Record if r.id == last_record)[:][0]) + [
                    ""])
            start = rnlist.index(last_roll_num) + 1
        else:
            start = from_num


    print("Starting the Brute Force Search from position {}".format(start))
    print("Process started at {}".format(time.strftime('%c')))

    for idx, rn in enumerate(rnlist[start:to_num]):
        if idx % 25 == 0:
            print("Downloading data for Roll No. {}".format("-".join(rn[:3])))
        visit(URL, rn, invalid=INVALID_RESULT, idx=idx)


download_data(options.start, options.end)
