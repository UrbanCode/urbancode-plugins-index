import os

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
PLUGIN_IMDEX_FOLDER="PLUGIN_IMDEX_FOLDER"

# info template field names

INFO_NAME="name"
INFO_DOCS="docs"
INFO_FILES="files"
INFO_DESCRIPTION="description"
INFO_PLUGIN_SPECIFICATION="specification"
INFO_AUTHOR="author"

# Plugin specification field names
PLUGIN_SPECIFICATION_CATEGORY="category"
PLUGIN_SPECIFICATION_TYPE="type"

# Author template field names
AUTHOR_NAME="name"
AUTHOR_EMAIL="email"

# Release template field anmes
RELEASE_VERSION="version" 
RELEASE_SEMVER="semver" 
RELEASE_DATE="date"  
RELEASE_FILE="file"
RELEASE_NOTES="notes"
RELEASE_SUPPORTS="supports"

# Author details, default to urbancode
def get_author_template():
    return {
        AUTHOR_NAME: "urbancode",
        AUTHOR_EMAIL: "urbancode-plugin@urbancode.com"
    }

# category: SCM, Source, Automation, ..
# type: OSS, PARTNER, IBM, ..
def get_plugin_specification_template():
    return {
        PLUGIN_SPECIFICATION_CATEGORY: "",
        PLUGIN_SPECIFICATION_TYPE: ""
    }

def get_info_template():
    return {
        INFO_NAME: "",
        INFO_DOCS: "",
        INFO_FILES: "",
        INFO_DESCRIPTION: "",
        INFO_PLUGIN_SPECIFICATION: get_plugin_specification_template(),
        INFO_AUTHOR: get_author_template()

    }

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
        PLUGIN_IMDEX_FOLDER: os.getenv(PLUGIN_IMDEX_FOLDER, "")
    }

def main():

    print ("Utility Functions for urbancode.com migration project")    
    os._exit(0)

if __name__ == '__main__':
    #main(sys.argv[1:])
    main()
    