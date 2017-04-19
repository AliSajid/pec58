"""
This file contains the basic code to download and store all the data for the 5th and 8th class exam from the Punjab Education Commission
Website. This site achieves that by doing the following:

1. It runs through the entire list of possible roll numbers from '00-000-000' to '99-999-999'.
2. After every page load, it checks if a result was returned. If it was, it stores that result into a local sqplite db indexed
by the roll number, otherwise it commits a NULL to it.
3. After the run is complete, it takes the db and processes the data.
"""
import logging
import pickle
import random
import time
from collections import namedtuple
from optparse import OptionParser
from os import path

from pony import orm
from requests import post

# Random wait time
distribution = list(range(1000, 5001, 500))
wait = random.choice(distribution)

# Setting up the option parser
parser = OptionParser()

parser.add_option("-s", "--start-num", dest="start", type="int", default=0)
parser.add_option("-e", "--end-num", dest="end", type="int", default=10000000)
(options, args) = parser.parse_args()

# Setting up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d-%Y %H:%M:%S,',
                    filename=path.join("logs", "data-{:0>8}-{:0>8}.log".format(options.start, options.end)),
                    filemode='a'
                    )
logger = logging.getLogger(__name__)

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# set a format which is simpler for console use
formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')

# tell the handler to use this format
console.setFormatter(formatter)

# add the handler to the root logger
logger.addHandler(console)

# Named tuple for RollNo
RollNo = namedtuple("RollNo", ['roll_no1', 'roll_no2', 'roll_no3', "search"])

# Database Setup
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


def generate_rollnums():
    filename = "rollnums.pickle"
    rn1 = [str(x).zfill(2) for x in range(0, 100)]
    rn2 = [str(x).zfill(3) for x in range(0, 1000)]
    rn3 = [str(x).zfill(3) for x in range(0, 1000)]

    rollnums = [RollNo(a, b, c, "") for a in rn1 for b in rn2 for c in rn3]
    with open(filename, 'wb') as f:
        pickle.dump(rollnums, f)
    return rollnums

@orm.db_session
def visit(url, rollno, invalid, idx):
    """
    This method visits the given site, fills the form, checks if a valid result is generated, adds the valid result 
    and the valid roll number to the valid dict and valid list respectively.

    :param url: 
    :param rollno: 
    :param invalid: 
    """
    try:
        res = post(url, rollno._asdict())
        if res.text.find(invalid) != -1:
            Record(rollno1=rollno[0], rollno2=rollno[1], rollno3=rollno[2], html="NULL", error=True, idx=idx)
        else:
            Record(rollno1=rollno[0], rollno2=rollno[1], rollno3=rollno[2], html=res.text, error=False, idx=idx)
    except Exception as e:
        logger.error(str(e))
        Record(rollno1=rollno[0], rollno2=rollno[1], rollno3=rollno[2], html="NULL", error=True, idx=idx)

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

def download_data(bounds, listfile=rollnums.pickle):
    (from_num, to_num) = bounds

    if path.isfile(listfile):
        with open(listfile, 'rb') as f:
            RNLIST = pickle.load(f)
    else:
        RNLIST = generate_rollnums()

    URL = "http://pec.edu.pk"
    INVALID_RESULT = "No Result found"

    logger.info("Start Parameter is: {}".format(from_num))
    logger.info("End Parameter is: {}".format(to_num))
    logger.info("Saving data to database {}".format(DBNAME))

    try:
        with orm.db_session:
            last_record = orm.max(r.id for r in Record)

            if last_record == to_num:
                logger.info("No new data to download. Exiting...")
                return

            if last_record:
                last_idx = orm.select(r.idx for r in Record if r.id == last_record)[:][0]
                start = last_idx + 1
            else:
                start = from_num

        logger.info("Starting the Brute Force Search from position {}".format(start))
        logger.info("Process started at {}".format(time.strftime('%c')))

        for idx, rn in enumerate(RNLIST[start:to_num]):
            if idx % wait == 0: time.sleep(5)
            if idx % 10 == 0:
                logger.info("Downloading data for Roll No. {}".format("-".join(rn[:3])))
            logger.info("Downloading Roll No. {}".format("-".join(rn[:3])))
            visit(URL, rn, invalid=INVALID_RESULT, idx=RNLIST.index(rn))
        logger.info("Process ended at {}".format(time.strftime('%c')))
    except KeyboardInterrupt as e:
        logger.error(str(e))
        logger.error("Recieved Keyboard Interrupt. Exiting.")

if __name__ == '__main__':
    download_data((options.start, options.end))
