import os
import logging

script_name = "uc_plugin_utilities"

logging.basicConfig()
logging.root.setLevel(logging.DEBUG)
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler(f"{script_name}.log", 'w+')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
lformat=logging.Formatter("[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

fh.setFormatter(lformat)
ch.setFormatter(lformat)
#logger1 = logging.getLogger(script_name)
logger1 = logging.getLogger(script_name)

logger1.addHandler(fh)
logger1.addHandler(ch)

# Plug-In documentation settings
PLUGIN_DOCS_ROOT="PLUGIN_DOCS_ROOT"
PLUGIN_DOCS_REPO="PLUGIN_DOCS_REPO"

PLUGIN_DOCS_FOLDER="PLUGIN_DOCS_FOLDER"
PLUGIN_DOCS_FILES_FOLDER="PLUGIN_DOCS_FILES_FOLDER"

# Plug-in files settings
UCD_PLUGIN_FILES_REPO="UCD_PLUGIN_FILES_REPO"
UCV_PLUGIN_FILES_REPO="UCV_PLUGIN_FILES_REPO"
UCR_PLUGIN_FILES_REPO="UCR_PLUGIN_FILES_REPO"
UCB_PLUGIN_FILES_REPO="UCB_PLUGIN_FILES_REPO"

UCX_PLUGIN_FILES_FOLDER="UCX_PLUGIN_FILES_FOLDER"

# target repo

PLUGIN_INDEX_REPO="PLUGIN_INDEX_REPO"
PLUGIN_INDEX_ROOT="PLUGIN_INDEX_ROOT"
PLUGIN_INDEX_FOLDER="PLUGIN_INDEX_FOLDER"

# name of the folder which will contain all media files. is used in each plugin folder!
PLUGIN_DOCS_MEDIA_FOLDER_NAME="media"


def get_config():
    return {
        PLUGIN_DOCS_ROOT: os.getenv(PLUGIN_DOCS_ROOT, ""),
        PLUGIN_DOCS_FOLDER: os.getenv(PLUGIN_DOCS_FOLDER, ""),
        PLUGIN_DOCS_FILES_FOLDER: os.getenv(PLUGIN_DOCS_FILES_FOLDER, ""),
        PLUGIN_DOCS_REPO: os.getenv(PLUGIN_DOCS_REPO, ""),
        UCD_PLUGIN_FILES_REPO: os.getenv(UCD_PLUGIN_FILES_REPO, ""),
        UCV_PLUGIN_FILES_REPO: os.getenv(UCV_PLUGIN_FILES_REPO, ""),
        UCR_PLUGIN_FILES_REPO: os.getenv(UCR_PLUGIN_FILES_REPO, ""),
        UCB_PLUGIN_FILES_REPO: os.getenv(UCB_PLUGIN_FILES_REPO, ""),
        UCX_PLUGIN_FILES_FOLDER: os.getenv(UCX_PLUGIN_FILES_FOLDER, ""),
        PLUGIN_INDEX_REPO: os.getenv(PLUGIN_INDEX_REPO, ""),
        PLUGIN_INDEX_ROOT: os.getenv(PLUGIN_INDEX_ROOT, ""),
        PLUGIN_INDEX_FOLDER: os.getenv(PLUGIN_INDEX_FOLDER, "")
    }

def main():

    print ("Utility Functions for urbancode.com migration project")    
    os._exit(0)

if __name__ == '__main__':
    #main(sys.argv[1:])
    main()
    