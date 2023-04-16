import os
import logging
import sys
import json
from zipfile import ZipFile
import xmltodict
import zipfile
import pathlib
import datetime

sys.path.append('/Users/ozzy/RnD/Source/PLUGINS/urbancode-plugins-index/src/helper/')
sys.path.append('/Users/ozzy/RnD/Source/PLUGINS/urbancode-plugins-index/src/helper/docs-helper')

import uc_plugin_utilities as ucutil
import uc_docs_utilities as docutil 


script_name = "create_workfile"

logging.basicConfig()
logging.root.setLevel(logging.INFO)
logging.basicConfig(format="[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")
logging.basicConfig(level=logging.INFO)

# create file handler which logs even debug messages
fh = logging.FileHandler(f"{script_name}.log", 'w+')
fh.setLevel(logging.INFO)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
lformat=logging.Formatter("[%(filename)s:%(lineno)s - %(funcName)20s() ] %(message)s")

fh.setFormatter(lformat)
ch.setFormatter(lformat)
logger1 = logging.getLogger(script_name)


logger1.addHandler(fh)
logger1.addHandler(ch)

def get_extended_release_template():

    extended_template=docutil.get_release_template()
    extended_template[docutil.INFO_DESCRIPTION] = ""
    return extended_template

# generator function to iterate over files in path
def get_files(path):
    for file in os.listdir(path):
        if os.path.isfile(os.path.join(path, file)):
            yield file

def get_plugin_dir_names(src):
    # getting the absolute path of the source
    # directory
    src = os.path.abspath(src)
    logger1.info(f"Source: {src}")

    list_subfolders_with_paths = [f.name for f in os.scandir(src) if f.is_dir()]
    return sorted(list_subfolders_with_paths)

# try to find the plug-in type
# either text is found " is a community plug-in" or "This plug-in is developed and supported by the UrbanCode Deploy Community" or "This community supported plug-in " or "is a community supported plug-in"
# or for partner "This is a partner plug-in" or "This is a partner provided plugin."

def get_plugin_specification(docs_path):
    plugin_specification = docutil.get_plugin_specification_template()

    community_indicator=["is a community plug-in", "This plug-in is developed and supported by the UrbanCode Deploy Community", "community supported plug-in", "This plug-in is developed and supported by the UrbanCode Build Community"]
    partner_indicator=["This is a partner plug-in", "This is a partner provided plugin"]

    filename= f"{docs_path}/README.md"
    source_repo_url = ""
    with open(filename) as file:
        for line in file:
            if bool([x for x in community_indicator if (x in line)]):
                plugin_specification[docutil.PLUGIN_SPECIFICATION_TYPE] = docutil.PLUGIN_TYPE_COMMUNITY
                break
            if bool([x for x in partner_indicator if (x in line)]):
                plugin_specification[docutil.PLUGIN_SPECIFICATION_TYPE] = docutil.PLUGIN_TYPE_PARTNER
                break

    return plugin_specification

def remove_new_lines(value):
    return ''.join(value.splitlines())

def get_release_notes (doc, semver):
    logger1.debug(f"doc={doc}")
    version = str(semver.split(".")[0])
    logger1.debug(f"version={version}")

    release_notes = []
    raw_release_notes = doc.get("pluginInfo", {}).get("release-notes", {}).get("release-note", "")
    logger1.debug(f"raw_release_notes={raw_release_notes}")

    # some files do not have an array
    if not(raw_release_notes): return []

    if not (isinstance(raw_release_notes, list)):
        if (str(raw_release_notes.get('@plugin-version', "")) == version): 
            release_notes = raw_release_notes.get('#text', "").splitlines()
    else:
        for release_note in raw_release_notes:
            logger1.debug(f"release_note={release_note}")
            if (str(release_note.get('@plugin-version', "")) == version): 
                release_notes = release_note.get('#text', "").splitlines()

    logger1.debug(f"release_notes{release_notes}")
    return release_notes

def get_tool_description(doc, existing_tool_description):
    tool_description = ""
    tool_description = doc.get("pluginInfo", {}).get("tool-description", existing_tool_description) 

    logger1.debug (f"desc={tool_description}")
    return tool_description
    
def get_semver_and_version(doc):
    semver = "0.0"
    version = "0"

    semver=doc.get("pluginInfo", {}).get("release-version", "0.0")
    logger1.debug (f"semver={semver}")
    
    if (semver): version = str(semver.split(".")[0])
    logger1.debug (f"infoxml.version={version}")

    return semver, version

def get_version_from_manifest(doc):

    return "0"
    # do not use...
    version = doc.get("pluginInfo", {}).get("versions", {}).get("version_name", "0")
    logger1.debug (f"version={version}")
    if int(version) < 0:
        logger1.debug(f"version < 0 {version}")

    return version 

def get_integration_type(doc):

    # try integrationType found in manfest.xml
    integration_type = integration_type = doc.get("pluginInfo", {}).get("integrationType", "")
    logger1.debug (f"integration_type={integration_type}")
    # try integrationType found in info.xml
    # integration type 'integration': {'@type': 'Build'},
    if (not integration_type): 
        integration=doc.get("pluginInfo", {}).get("integration", "")
        logger1.debug (f"integration={integration}")
        if (integration): integration_type = integration.get("@type", "")

    logger1.debug (f"integration_type={integration_type}")
    return integration_type

def get_categories(doc):
    list_of_category = []
    categories=doc.get("pluginInfo", {}).get("categories", "")
    logger1.debug (f"categories={categories}")
    if (categories): list_of_category=categories.get("category", [])
    return list_of_category

def get_content_from_file(file, zf):
    doc = {"pluginInfo": {'tool-description': "ERROR FILE DAMAGED"}}
    logger1.debug(f"accessing {file}")
    try:
        xfile=zf.read(file)
    except zipfile.BadZipFile as ex:
        logger1.warn(f"file is not good={file}")
        return doc
    
    # special work with hpi files and manifest.mf
    if (file=="META-INF/MANIFEST.MF"):
        logger1.info(f"content of manifest.mf={xfile}")
        decoded_string = xfile.decode('utf-8')

        dictionary = {}
        for line in decoded_string.split('\r\n'):
            if line.strip() != '':
                key, value = line.split(': ', maxsplit=1)
                dictionary[key] = value
        doc = dictionary
    else:
        doc = xmltodict.parse(xfile)
    
    logger1.info(f"doc={doc}")
    
    return doc 

def get_info_from_zip_file(plugin_path, file):
    file_with_path = f"{plugin_path}/{file}"
    logger1.info(f"file_with_path={file_with_path}")

    file_info = get_extended_release_template()

    # if file extension is 00x then it is packed with 7zip -> extract and use extracted file for processing
    # TODO: implement handling of 7ziped files

    # when not a zipfile return with info
    # version info is "" also an indicator
    file_info[docutil.RELEASE_FILE]=file
    if (not zipfile.is_zipfile(file_with_path)):
        file_info[docutil.INFO_DESCRIPTION]="NOT PLUGIN FILE"
        return file_info

    # special handling for .hpi
    # META-INF/MANIFEST.MF
        # Manifest-Version: 1.0
        # Archiver-Version: Plexus Archiver
        # Created-By: Apache Maven
        # Built-By: anthill
        # Build-Jdk: 1.7.0
        # Extension-Name: ibm-ucrelease-pipeline
        # Specification-Title: The Jenkins Plugins Parent POM Project
        # Implementation-Title: ibm-ucrelease-pipeline
        # Implementation-Version: 1.919098
        # Group-Id: com.urbancode.jenkins.plugins
        # Short-Name: ibm-ucrelease-pipeline
        # Long-Name: IBM UrbanCode Release Pipeline Plugin
        # Url: https://developer.ibm.com/urbancode/plugin/jenkins/
        # Plugin-Version: 1.919098
        # Hudson-Version: 1.625.3
        # Jenkins-Version: 1.625.3
        # Plugin-Dependencies: workflow-step-api:1.15
        # Plugin-Developers: 

    if (".hpi" in file_with_path):
        with ZipFile(file_with_path, 'r') as zf:
            logger1.info(f"file_list of hpi={zf.infolist()}")
            doc = get_content_from_file("META-INF/MANIFEST.MF", zf)
            logger1.info (f" hpi content MANIFEST.MF = {doc}")
        return file_info
    with ZipFile(file_with_path, 'r') as zf:
        for file in zf.infolist():
            logger1.debug(f"file={file}")
            if file.filename == "info.xml":
                doc = get_content_from_file(file.filename, zf)

                zipfileinfo=zf.getinfo(file.filename).date_time
                logger1.debug(f"zipfileinfo={zipfileinfo}")
                file_info_datetime = datetime.datetime(*zipfileinfo)
                
                logger1.debug(f"zipfileinfodatetimestring={file_info_datetime.strftime('%Y.%m.%d %H:%M')}")
                file_info[docutil.RELEASE_DATE]=file_info_datetime.strftime('%Y.%m.%d %H:%M')
                
                file_info[docutil.INFO_DESCRIPTION] = get_tool_description(doc, file_info[docutil.INFO_DESCRIPTION])

                file_info[docutil.RELEASE_SEMVER], file_info[docutil.RELEASE_VERSION] = get_semver_and_version(doc)

                file_info[docutil.PLUGIN_SPECIFICATION_TYPE] = get_integration_type(doc)

                # release notes
                file_info[docutil.RELEASE_NOTES] = get_release_notes(doc, file_info[docutil.RELEASE_SEMVER])
                

            if file.filename == "manifest.xml":
                doc = get_content_from_file(file.filename, zf)

                file_info[docutil.PLUGIN_SPECIFICATION_TYPE] = get_integration_type(doc)

                file_info[docutil.PLUGIN_SPECIFICATION_CATEGORIES] = get_categories(doc)


    logger1.debug(f"file_info={file_info}")
    return file_info

def get_list_and_info_of_plugin_files(plugin_path):
    logger1.debug(f"{plugin_path}")
    files=[]
    for file in get_files(plugin_path):
        # if zipfile extension is 002 or higher than it is zipped with 7zip and process only 001 
        file_extension = pathlib.Path(file).suffix
        if (file_extension in [".002", ".003", ".004", ".005"]):
            continue
        file_info = get_extended_release_template()
        file_info[docutil.RELEASE_FILE]=file
        temp_info=get_info_from_zip_file(plugin_path,file)
        logger1.debug(f"temp_info={temp_info}")
        for key, value in temp_info.items():
            file_info[key] = value

        files.append(file_info)
        logger1.debug(f"fles={files}")

    # my_list = sorted(my_list, key=lambda k: k['name'])
    if files:
        files = sorted(files, key=lambda k: int(k["version"]))
    return files

def get_list_of_all_names(docs, files):
    listofplugins=[]

    all_plugin_doc_dir_names=get_plugin_dir_names(docs)
    all_plugin_files_dir_name=get_plugin_dir_names(files)

    # iterate first over doc folders

    for docitem in all_plugin_doc_dir_names:
        oneplugin=docutil.get_info_template()
        oneplugin[docutil.INFO_NAME] = docutil.get_title_from_file(f"{docs}/{docitem}/README.md")
        oneplugin[docutil.INFO_DOCS_FOLDER] = docitem
        oneplugin["NEW_FOLDER_NAME"]=str(docitem).lower()
        if (docitem in all_plugin_files_dir_name):
            # oneplugin[docutil.INFO_NAME] = docitem
            oneplugin[docutil.INFO_PLUGIN_FOLDER] = docitem
            oneplugin["PLUGIN_FILES"]=get_list_and_info_of_plugin_files(f"{files}/{docitem}")
        else:
            oneplugin[docutil.INFO_SOURCE_PROJECT] = docutil.get_source_repository_from_file(f"{docs}/{docitem}/README.md")
            oneplugin[docutil.INFO_PLUGIN_SPECIFICATION] = get_plugin_specification(f"{docs}/{docitem}")
        
        logger1.debug(f"oneplugin={oneplugin}")
        listofplugins.append(oneplugin)

    for plugitem in all_plugin_files_dir_name:
        if (plugitem not in all_plugin_doc_dir_names):
            oneplugin=docutil.get_info_template()
            oneplugin[docutil.INFO_NAME] = "DOCS-NOT-FOUND"
            oneplugin[docutil.INFO_PLUGIN_FOLDER] = plugitem
            oneplugin["PLUGIN_FILES"]=get_list_and_info_of_plugin_files(f"{files}/{plugitem}")
            listofplugins.append(oneplugin)        
    return listofplugins

def get_workfile(config):

    UCB_Docs = f"{config[ucutil.PLUGIN_DOCS_ROOT]}/{config[ucutil.PLUGIN_DOCS_FOLDER]}/UCB"
    UCB_Files = f"{config[ucutil.UCB_PLUGIN_FILES_ROOT]}/{config[ucutil.UCX_PLUGIN_FILES_FOLDER]}"
    UCD_Docs = f"{config[ucutil.PLUGIN_DOCS_ROOT]}/{config[ucutil.PLUGIN_DOCS_FOLDER]}/UCD"
    UCD_Files = f"{config[ucutil.UCD_PLUGIN_FILES_ROOT]}/{config[ucutil.UCX_PLUGIN_FILES_FOLDER]}"
    UCR_Docs = f"{config[ucutil.PLUGIN_DOCS_ROOT]}/{config[ucutil.PLUGIN_DOCS_FOLDER]}/UCR"
    UCR_Files = f"{config[ucutil.UCR_PLUGIN_FILES_ROOT]}/{config[ucutil.UCX_PLUGIN_FILES_FOLDER]}"
    UCV_Docs = f"{config[ucutil.PLUGIN_DOCS_ROOT]}/{config[ucutil.PLUGIN_DOCS_FOLDER]}/UCV"
    UCV_Files = f"{config[ucutil.UCV_PLUGIN_FILES_ROOT]}/{config[ucutil.UCX_PLUGIN_FILES_FOLDER]}"


    adict = {
            "UCB" : [], # get_list_of_all_names(UCB_Docs, UCB_Files),
            "UCD" : [], # get_list_of_all_names(UCD_Docs, UCD_Files),
            "UCR" : get_list_of_all_names(UCR_Docs, UCR_Files),
            "UCV" : [] # get_list_of_all_names(UCV_Docs, UCV_Files)
            }


    return adict

def main():
    config = ucutil.get_config()

    adict = get_workfile(config)
    logger1.debug(f"adict={adict}")

    with open (f"list.json", "w") as f:
        json.dump(adict,f, indent=4)
if __name__ == '__main__':
    main()
                