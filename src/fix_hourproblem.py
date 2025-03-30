import logging
import json

#sys.path.append('/Users/ozzy/RnD/Source/PLUGINS/urbancode-plugins-index/src/helper')
from helper import uc_docs_utilities as docutil 
from helper import uc_plugin_utilities as ucutil

SCRIPT_NAME = "fix_hourproblem"
LOG_LEVEL=logging.INFO

logging.basicConfig()
logging.root.setLevel(LOG_LEVEL)
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=LOG_LEVEL)

# create file handler which logs even debug messages
fh = logging.FileHandler(f"{SCRIPT_NAME}.log", 'w+')
fh.setLevel(LOG_LEVEL)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(LOG_LEVEL)
lformat=logging.Formatter("[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

fh.setFormatter(lformat)
ch.setFormatter(lformat)
logger1 = logging.getLogger(SCRIPT_NAME)


logger1.addHandler(fh)
logger1.addHandler(ch)

def getfixedhour(read_data: dict, product: str) -> dict:
    logger1.info(f"Product={product}")
    plugins = read_data.get(product)
    for plugin in plugins:
        logger1.info(f"Plugin={plugin.get(docutil.INFO_NAME)}")
        for plugin_file in plugin.get(ucutil.PLUGIN_FILES, []):
            logger1.info(f"plugin_files={plugin_file}")
            logger1.info(f"date={plugin_file.get(docutil.RELEASE_DATE)}")
    return read_data

def main():
    for product in ["UCB", "UCD", "UCR"]:                         # ["UCR", "UCV"]: #["UCB", "UCD", "UCR", "UCV"]:
        read_data = json.load(open(f"{product}-list.json", "r"))
        adict=getfixedhour(read_data, product)
#        with open(f"{product}-list.json", "w") as f:
#            json.dump(adict,f, indent=4)

if __name__ == '__main__':
    main()
                