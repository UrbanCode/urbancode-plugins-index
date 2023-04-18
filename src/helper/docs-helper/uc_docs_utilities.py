import os
import logging
import pathlib
import markdown

script_name="uc_docs_utility"
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


# Detailed object definitions
# Release template field names
RELEASE_VERSION="version" 
RELEASE_SEMVER="semver" 
RELEASE_DATE="date"  
RELEASE_FILE="file"
RELEASE_NOTES="notes"
RELEASE_SUPPORTS="supports"

PUBLISH = "publish"

# Version and Semver could be different
# Date is ISO date YYYY-MM-DDTHH:mm:SS.hhhZ
# File is the filename
# Notes is list of strings
# Supports defines minimum supported version of product
def get_release_template():
    return {
        RELEASE_VERSION:"0", 
        RELEASE_SEMVER:"0.0", 
        RELEASE_DATE:"",  
        RELEASE_FILE:"",
        RELEASE_NOTES:[],
        RELEASE_SUPPORTS:"",
        PUBLISH: True
    }

# Author template field names
AUTHOR_NAME="name"
AUTHOR_EMAIL="email"

# Author details, default to urbancode
def get_author_template():
    return {
        AUTHOR_NAME: "",
        AUTHOR_EMAIL: ""
    }

# Plugin specification field names
PLUGIN_SPECIFICATION_CATEGORIES="categories"
PLUGIN_SPECIFICATION_TYPE="type"

# category: SCM, Source, Automation, ..
# type: OSS, PARTNER, IBM, ..
def get_plugin_specification_template():
    return {
        PLUGIN_SPECIFICATION_CATEGORIES: [],
        PLUGIN_SPECIFICATION_TYPE: ""
    }

PLUGIN_TYPE_COMMUNITY="Community"
PLUGIN_TYPE_PARTNER="Partner"
PLUGIN_TYPE_DEFAULT="IBM"

# info template field names
INFO_NAME="name"
INFO_DOCS_FOLDER="docs_folder"
INFO_DOCS_URL="docsURL"
INFO_PLUGIN_FOLDER="plugin_folder"
INFO_SOURCE_PROJECT="source_project"
INFO_DESCRIPTION="description"
INFO_PLUGIN_SPECIFICATION="specification"
INFO_AUTHOR="author"
INFO_FILES="files"
INFO_DOC_FILES="docFiles"

def get_info_template():
    return {
        INFO_NAME: "",
        INFO_DOCS_FOLDER: "",
        INFO_DOCS_URL: "",
        INFO_PLUGIN_FOLDER:"",
        INFO_SOURCE_PROJECT: "",
        INFO_DESCRIPTION: "",
        INFO_PLUGIN_SPECIFICATION: get_plugin_specification_template(),
        INFO_AUTHOR: get_author_template(),
        PUBLISH: True
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
        DOCFILE_SUB_DOCUMENTS:[],
        DOCFILE_FOLDER_NAME:""
    }

# 

# get Info name from header of README.md

def get_title_from_file(filename):
    logger1.debug (f"File={filename}")
    title= ""
    lines=[]
    with open(filename) as myfile:
        lines = myfile.readlines()[:5]

    for line in lines:
        logger1.debug(f"line={line}")
        if line.startswith("#"):
            title = line.strip("#").strip()  # remove "#" and any additional whitespace
            logger1.info (f"title={title}")
            break

    if title=="":
        titlefound = False
        for line in reversed(lines):
            if titlefound: 
                title = line.strip()
                break
            if line.startswith("="):
                titlefound = True
    return title

def get_source_repository_from_file(filename):
    source_repo_url = ""
    with open(filename) as file:
       for line in file:
        if "[Source project](" in line:
            print ("found the line")
            splitted = line.split("[Source project](")
            source_repo_url = splitted[1].strip()[:-1]
            break
    return source_repo_url

def get_name_from_filename(filename):

    # all README's have same name "Readme"
    temp = filename.split(".md")
    splitted_file_name = temp[0].split(" ")

    docfilename = ""
    for x in splitted_file_name:
        if (x != "and"): x=x.capitalize()
        docfilename = f"{docfilename} {x}"

    return docfilename.strip()

    # logger1.debug(f"mddata={mddata}")
    # splitted=mddata.split("\n")
    # checkindex=0
    # logger1.debug(f"splitted[checkindex]={splitted[checkindex]}")
    # logger1.debug(f"length of splitted[checkindex]={len(splitted[checkindex].strip())}")

    # if len(splitted[checkindex].strip())==0: checkindex +=1
    # headerline=splitted[checkindex].replace("#", "").strip()
    # logger1.debug(f"headerline={headerline}")

    # splitted2=headerline.split("-")
    # logger1.debug(f"splitted2={splitted2}")

    # plugin_name=splitted2[0].strip()
    # logger1.debug(f"plugin_name={plugin_name}")
    # docfilename = splitted2[1].strip() if len(splitted2) > 1 else "Readme"
    # logger1.debug(f"docfilename={docfilename}")
    # # os.exit(1)
    # return docfilename

def get_docfile_info(docfile_path, filename, docfile_folder=""):
    docfile_info=get_docfile_template()

    if ("/" in filename):
        splitted_file_name = filename.split("/")
        docfile_info[DOCFILE_FOLDER_NAME] = "".join(splitted_file_name[:-1])
        docfile_info[DOCFILE_FILE_NAME] = splitted_file_name[-1]
        logger1.info(f"splitted_file_name={splitted_file_name}")
    else:
        docfile_info[DOCFILE_FILE_NAME]=filename
        docfile_info[DOCFILE_FOLDER_NAME]=docfile_folder

    if ".md" not in filename: return docfile_info

    fdata=pathlib.Path(os.path.join(docfile_path, filename)).read_text(encoding='utf-8')
    mdmeta=markdown.Markdown(extensions=['meta'])
    mdmeta.convert(fdata)
    # as the markdownfiles do not contain metadata, we need to get them from header data

    docfile_info[DOCFILE_NAME]=get_name_from_filename(filename)
    return docfile_info 

def get_info(plugin_path):
    # get the plug-in name from README.md from plugin_path
    logger1.info(f"passed plugin_path={plugin_path}")

    dir_list=os.listdir(plugin_path)
    logger1.info(f"dir_list={dir_list}")

    plugin_info=get_info_template()
    plugin_dir = pathlib.PurePath(plugin_path)
    plugin_info[INFO_NAME] = plugin_dir.name
    
    for dir_item in dir_list:
        if dir_item == "media": continue
        if ".md" in dir_item:
            docfile_info=get_docfile_info(plugin_path, dir_item)
            plugin_info[INFO_FILES].append(docfile_info)
    # for root, dirs, files in os.walk(plugin_path):

    #     # if dirs is empty then iterate over files
    #     # else it is either the media dir or subdir 
    #     logger1.info(f"root={root}")
    #     if ("media" in root): continue
    #     if (dirs):
    #         for dir in dirs:
    #             # if dir is media, ignore else
    #             # add to subdir in subdocs list?
    #             logger1.info(f"dir={dir}")
    #     else:
    #         for file in files:
    #         # # if readme - get plugin file name
    #         # # else add to list of docs?
    #             logger1.info(f"dir/file={plugin_path}/{file}")            

    return plugin_info

def main():

    print ("Utility Functions for urbancode documentation project")    
    os._exit(0)

if __name__ == '__main__':
    #main(sys.argv[1:])
    main()
    