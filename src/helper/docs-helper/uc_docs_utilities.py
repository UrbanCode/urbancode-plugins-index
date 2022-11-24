import os
import logging


logging.basicConfig()
logging.root.setLevel(logging.DEBUG)
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=logging.DEBUG)

# create file handler which logs even debug messages
fh = logging.FileHandler(f"{__name__}.log", 'w+')
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
lformat=logging.Formatter("[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

fh.setFormatter(lformat)
ch.setFormatter(lformat)
#logger1 = logging.getLogger(script_name)
logger1 = logging.getLogger(__name__)

logger1.addHandler(fh)
logger1.addHandler(ch)


# Detailed object definitions
# Release template field names
RELEASE_VERSION="version" 
RELEASE_SEMVER="semver" 
RELEASE_DATE="date"  
RELEASE_FILE="file"
RELEASE_NOTES="notes"
RELEASE_SUPPORTS="supports"

# Version and Semver could be different
# Date is ISO date YYYY-MM-DDTHH:mm:SS.hhhZ
# File is the filename
# Notes is list of strings
# Supports defines minimum supported version of product
def get_release_template():
    return {
        RELEASE_VERSION:"", 
        RELEASE_SEMVER:"", 
        RELEASE_DATE:"",  
        RELEASE_FILE:"",
        RELEASE_NOTES:[""],
        RELEASE_SUPPORTS:""
    }

# Author template field names
AUTHOR_NAME="name"
AUTHOR_EMAIL="email"

# Author details, default to urbancode
def get_author_template():
    return {
        AUTHOR_NAME: "urbancode",
        AUTHOR_EMAIL: "urbancode-plugin@urbancode.com"
    }

# Plugin specification field names
PLUGIN_SPECIFICATION_CATEGORY="category"
PLUGIN_SPECIFICATION_TYPE="type"

# category: SCM, Source, Automation, ..
# type: OSS, PARTNER, IBM, ..
def get_plugin_specification_template():
    return {
        PLUGIN_SPECIFICATION_CATEGORY: "",
        PLUGIN_SPECIFICATION_TYPE: ""
    }

# info template field names
INFO_NAME="name"
INFO_DOCS="docs"
INFO_DOCS_URL="docsURL"
INFO_FILES="files"
INFO_PLUGIN_FOLDER="pluginFolder"
INFO_DESCRIPTION="description"
INFO_PLUGIN_SPECIFICATION="specification"
INFO_AUTHOR="author"
INFO_DOC_FILES="docFiles"

def get_info_template():
    return {
        INFO_NAME: "",
        INFO_DOCS: "",
        INFO_DOCS_URL: "",
        INFO_PLUGIN_FOLDER:"",
        INFO_FILES: [""],
        INFO_DESCRIPTION: "",
        INFO_PLUGIN_SPECIFICATION: get_plugin_specification_template(),
        INFO_AUTHOR: get_author_template()

    }

# Document files fieldnames. Can contain sub documents and will have same structure!
DOCFILE_NAME="name"
DOCFILE_FILE_NAME="file_name"
DOCFILE_SUB_DOCUMENTS="sub_documents"
# for sub documents
DOCFILE_FOLDER_NAME="folder_name"

def get_docfile_template():
    return {
        DOCFILE_NAME:"",
        DOCFILE_FILE_NAME:"",
        DOCFILE_SUB_DOCUMENTS:[""],
        DOCFILE_FOLDER_NAME:""
    }

def get_info(plugin_path):
    # get the plug-in name from README.md from plugin_path
    logger1.info(f"passed plugin_path={plugin_path}")
    for root, dirs, files in os.walk(plugin_path):

        # if dirs is empty then iterate over files
        # else it is either the media dir or subdir 

        if (dirs):
            for dir in dirs:
                # if dir is media, ignore else
                # add to subdir in subdocs list?
                logger1.info(f"dir={dir}")

        # for file in files:
        # # if readme - get plugin file name
        # # else add to list of docs?
        #     logger1.info(f"dir/file={dir}/{file}")            

    #return get_info_template()

def main():

    print ("Utility Functions for urbancode documentation project")    
    os._exit(0)

if __name__ == '__main__':
    #main(sys.argv[1:])
    main()
    