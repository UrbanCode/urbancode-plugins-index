import os
import logging
import sys
import json
from zipfile import ZipFile
import xmltodict
import zipfile
import pathlib
import datetime
import py7zr
import multivolumefile

#sys.path.append('/Users/ozzy/RnD/Source/PLUGINS/urbancode-plugins-index/src/helper')
from helper import uc_docs_utilities as docutil 
from helper import uc_plugin_utilities as ucutil


script_name = "create_workfile"

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
logger1 = logging.getLogger(script_name)


logger1.addHandler(fh)
logger1.addHandler(ch)

SORT_VERSION = "SORT_VERSION"
NEW_FOLDER_NAME = "NEW_FOLDER_NAME"
PLUGIN_FILES = "PLUGIN_FILES"
README = "README.md"
DOCS_NOT_FOUND = "DOCS_NOT_FOUND"

def get_extended_release_template():

    extended_template=docutil.get_release_template()
    extended_template[docutil.INFO_DESCRIPTION] = ""
    extended_template[SORT_VERSION] = ""
    return extended_template

# # generator function to iterate over files in path
# def get_files(path):
#     for file in os.listdir(path):
#         if os.path.isfile(os.path.join(path, file)):
#             yield file

def get_files_with_dirs(path):
    for (dir_path, dir_names, file_names) in os.walk(path):
        if file_names:
            newpath=dir_path.replace(f"{path}", "").replace("/", "")
            for file in file_names:
                yield f"{newpath}/{file}" if newpath else file

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

def get_plugin_specification(docs_path, ucproduct):
    plugin_specification = docutil.get_plugin_specification_template()

    community_indicator=["is a community plug-in", "This plug-in is developed and supported by the UrbanCode Deploy Community", "community supported plug-in", "This plug-in is developed and supported by the UrbanCode Build Community"]
    partner_indicator=["This is a partner plug-in", "This is a partner provided plugin"]

    if ucproduct == "UCV": return 
    
    filename= f"{docs_path}/{README}"
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

def get_release_notes(doc, semver):
    logger1.debug(f"doc={doc}")
    version = semver if "." not in semver else str(semver.split(".")[0])
    logger1.debug(f"version={version}")

    release_notes = []
    raw_release_notes = doc.get("pluginInfo", {}).get("release-notes", {}).get("release-note", "")
    logger1.debug(f"raw_release_notes={raw_release_notes}")

    # some files do not have an array
    if not(raw_release_notes): return []

    if (isinstance(raw_release_notes, list)):
        for release_note in raw_release_notes:
            logger1.debug(f"release_note={release_note}")
            if (str(release_note.get('@plugin-version', "")) == version): 
                release_notes = release_note.get('#text', "").splitlines()

    elif (str(raw_release_notes.get('@plugin-version', "")) == version): 
        release_notes = raw_release_notes.get('#text', "").splitlines()
    logger1.debug(f"release_notes{release_notes}")
    return release_notes

def get_tool_description(doc, existing_tool_description):
    tool_description = ""
    tool_description = doc.get("pluginInfo", {}).get("tool-description", existing_tool_description) 

    if (not tool_description): tool_description = ""
    logger1.debug (f"desc={tool_description}")
    return tool_description
    
def get_semver_and_version(semver):
    version = "0.0"
    sort_version = ""
    if semver:
        # there is an issue with text #RELEASE_VERSION# in semver
        if ("#RELEASE_VERSION#" in semver): semver = "0.0"
        if (semver.startswith(".")):
            semver = f"0.{semver}"
        version = semver
        numberofdots = semver.count(".")
        if (numberofdots > 0): 
            semverarray = semver.split(".")
            version = f"{semverarray[0]}"

        for idx, x in enumerate(semver.split(".")):
            if idx == 0: version = x
            sort_version = sort_version + x.zfill(8)
        # there are semver with missing first number -->  .2345
        if (not version): version = "0"
        # there
        if (not int(version)): version = "0"
    logger1.debug (f"infoxml.version={version}")

    return semver, version, sort_version

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
    categories=doc.get("pluginInfo", {}).get("categories", "")
    logger1.debug (f"categories={categories}")
    return categories.get("category", []) if categories else []

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
        logger1.debug(f"content of manifest.mf={xfile}")
        decoded_string = xfile.decode('utf-8')

        dictionary = {}
#        for line in decoded_string.split('\r\n'):
        for line in decoded_string.splitlines():
            if line.strip() != '':
                logger1.debug(f"line={line}")
                if ("," in line): 
                    for line2 in line.split(","):
                        if line.strip() != '':
                            logger1.debug(f"line2={line2}")
                            key, value = get_key_value_from_line(line)
                            dictionary[key] = value
                else:
                    key, value = get_key_value_from_line(line)
                    dictionary[key] = value
        doc = dictionary
    else:
        xfile=xfile.replace(b"'", b"") #replace(b"{", b"#curlybrace-open").replace(b"}", b"#curlybrace-close").
        doc = xmltodict.parse(xfile)
        logger1.debug(f"DOC = {doc}")
    
    logger1.debug(f"doc={doc}")
    
    return doc 

def get_key_value_from_line(line):
    if ":" in line: 
        key, value = line.split(':', maxsplit=1)
    else: 
        key = "UNKNOWN"
        value = line
    return key.strip(),value.strip()

def get_info_from_jenkins_plugin(zf, file_info):
    logger1.debug(f"file_list of hpi={zf.infolist()}")
    semver = "0.0"
    filename = "META-INF/MANIFEST.MF"
    doc = get_content_from_file(filename, zf)
    logger1.debug (f" hpi content MANIFEST.MF = {doc}")
    semver=doc.get("Plugin-Version", "0.0")
    logger1.debug (f"semver={semver}")

    file_info_datetime = get_release_date(zf, filename)
                
    logger1.debug(f"zipfileinfodatetimestring={file_info_datetime.strftime('%Y.%m.%d %H:%M')}")
    file_info[docutil.RELEASE_DATE]=file_info_datetime.strftime('%Y.%m.%d %H:%M')

    file_info[docutil.RELEASE_SEMVER], file_info[docutil.RELEASE_VERSION], file_info[SORT_VERSION] = get_semver_and_version(semver)

def is_standard_plugin(file_with_path) -> bool:
    standard_plugin = False
    with ZipFile(file_with_path, 'r') as zf:
        for file in zf.infolist():
            logger1.debug(f"file={file}")
            if file.filename == "info.xml": 
                standard_plugin = True
                break
    return standard_plugin

def get_info_from_standard_plugin(zf, file_info):
    for file in zf.infolist():
        logger1.debug(f"file={file}")
        if file.filename == "info.xml":
            get_info_from_infoxml(zf, file, file_info)

        if file.filename == "manifest.xml":
            get_info_from_manifestxml(zf, file, file_info)

def get_info_from_manifestxml(zf, file, file_info):
    doc = get_content_from_file(file.filename, zf)

    file_info[docutil.PLUGIN_SPECIFICATION_TYPE] = get_integration_type(doc)

    file_info[docutil.PLUGIN_SPECIFICATION_CATEGORIES] = get_categories(doc)

def get_info_from_infoxml(zf, file, file_info):
    doc = get_content_from_file(file.filename, zf)

    file_info_datetime = get_release_date(zf, file.filename)
                
    logger1.debug(f"zipfileinfodatetimestring={file_info_datetime.strftime('%Y.%m.%d %H:%M')}")
    file_info[docutil.RELEASE_DATE]=file_info_datetime.strftime('%Y.%m.%d %H:%M')
                
    file_info[docutil.INFO_DESCRIPTION] = get_tool_description(doc, file_info[docutil.INFO_DESCRIPTION])

    semver=doc.get("pluginInfo", {}).get("release-version", "0.0")
    logger1.debug (f"semver={semver}")
    file_info[docutil.RELEASE_SEMVER], file_info[docutil.RELEASE_VERSION], file_info[SORT_VERSION] = get_semver_and_version(semver)

    file_info[docutil.PLUGIN_SPECIFICATION_TYPE] = get_integration_type(doc)

    # release notes
    file_info[docutil.RELEASE_NOTES] = get_release_notes(doc, file_info[docutil.RELEASE_SEMVER])

def get_release_date(zf, filename):
    zipfileinfo=zf.getinfo(filename).date_time
    logger1.debug(f"zipfileinfo={zipfileinfo}")
    return datetime.datetime(*zipfileinfo)

def get_info_from_zip_file(plugin_path, file, file_info, ucproduct):
    file_with_path = f"{plugin_path}/{file}"
    logger1.info(f"file_with_path={file_with_path}")
    
    file_info[docutil.RELEASE_FILE]=file

    if ucproduct == "UCV": return

    ## special treatment for sample application
    if ("CreateCollectiveSampleApp.zip" in file_with_path):
        logger1.error("CreateCollectiveSample.zip handling needs to be implemented")
        file_info[docutil.RELEASE_FILE]=file
        file_info[docutil.INFO_DESCRIPTION]="NOT PLUGIN FILE - is a Sample"
        return
    # if file extension is 00x then it is packed with 7zip -> extract and use extracted file for processing
    # TODO: implement handling of 7ziped files
        
    if (".7z" in file_with_path):
        # need to extract using 7zip and then use new file name to get info...
        # file_with_path = extracted file with new path
        config = ucutil.get_config()
        

        # Open the multi-file 7zip archive

        # new_file_with_path = os.path.splitext(file_with_path)[0]
        # with multivolumefile.open(new_file_with_path, mode='rb') as target_archive:
        #     with py7zr.SevenZipFile(target_archive, 'r') as archive:
        #         archive.extractall()
        import subprocess

        # Run 7zip command to extract multi-file 7zip archive
        subprocess.run(['7z', 'x', file_with_path, f'-o{config[ucutil.ZIP_TEMP_DIR]}'])
        os.exit(0)
        return 

    # when not a zipfile return with info
    # version info is "" also an indicator
    file_info[docutil.RELEASE_FILE]=file
    if (not zipfile.is_zipfile(file_with_path)):
        file_info[docutil.INFO_DESCRIPTION]="NOT PLUGIN FILE"
        return

    with ZipFile(file_with_path, 'r') as zf:
        if (".hpi" in file_with_path):
            get_info_from_jenkins_plugin(zf, file_info) # get_info_from_jenkins_plugin(plugin_path, file, file_info)
        elif is_standard_plugin(file_with_path): 
            get_info_from_standard_plugin(zf, file_info)

    logger1.debug(f"file_info={file_info}")
    return


def get_all_doc_files(doc_path):
    logger1.info (f"docpath={doc_path}")
    listofdocfiles = []

    for file in get_files_with_dirs(doc_path):
        logger1.info(f"file={file}")
        docfile = docutil.get_docfile_info(doc_path, file)
        logger1.info(f"docfile={docfile}")
        listofdocfiles.append(docfile)
    
    return listofdocfiles

def get_list_and_info_of_plugin_files(plugin_path, ucproduct):
    logger1.debug(f"{plugin_path}")
    files=[]
    for file in get_files_with_dirs(plugin_path): #get_files(plugin_path):
        # if zipfile extension is 002 or higher than it is zipped with 7zip and process only 001 
        file_extension = pathlib.Path(file).suffix
        if file_extension in { ".002", ".003", ".004", ".005"}:
            # need to find a solution how to unpack .001 and use unzipped file for further processing.
            continue
        
        # do not add "._xxxx" type of files, are from mac os
        if (file.startswith("._")): continue

        file_info = get_extended_release_template()
        get_info_from_zip_file(plugin_path,file, file_info, ucproduct)
        # logger1.debug(f"temp_info={temp_info}")
        # for key, value in temp_info.items():
        #     file_info[key] = value

        files.append(file_info)

    # my_list = sorted(my_list, key=lambda k: k['name'])
    if files:
        logger1.debug (f"all files={files}")
        # files = sorted(files, key=lambda x: [int(i) if i.isnumeric() else int(i) for i in x["semver"].split('.')])
        files = sorted(files, key=lambda k: k[SORT_VERSION])
    return files

def get_list_of_all_names(docs, files, ucproduct):
    listofplugins=[]

    all_plugin_doc_dir_names=get_plugin_dir_names(docs)
    all_plugin_files_dir_name=get_plugin_dir_names(files)

    # iterate first over doc folders

    for docitem in all_plugin_doc_dir_names:
        oneplugin=docutil.get_info_template()
        oneplugin[docutil.INFO_NAME] = docutil.get_title_from_file(f"{docs}/{docitem}/{README}")
        oneplugin[docutil.INFO_DOCS_FOLDER] = docitem
        oneplugin[NEW_FOLDER_NAME]=str(docitem).lower()
        if (docitem in all_plugin_files_dir_name):
            # oneplugin[docutil.INFO_NAME] = docitem
            oneplugin[docutil.INFO_PLUGIN_FOLDER] = docitem
            oneplugin[PLUGIN_FILES]=get_list_and_info_of_plugin_files(f"{files}/{docitem}", ucproduct)
        else:
            oneplugin[docutil.INFO_SOURCE_PROJECT] = docutil.get_source_repository_from_file(f"{docs}/{docitem}/{README}")
            oneplugin[docutil.INFO_PLUGIN_SPECIFICATION] = get_plugin_specification(f"{docs}/{docitem}", ucproduct)
        
        oneplugin[docutil.INFO_DOC_FILES] = get_all_doc_files(f"{docs}/{docitem}")
        logger1.debug(f"oneplugin={oneplugin}")
        listofplugins.append(oneplugin)

    for plugitem in all_plugin_files_dir_name:
        if (plugitem not in all_plugin_doc_dir_names):
            oneplugin=docutil.get_info_template()
            oneplugin[docutil.INFO_NAME] = DOCS_NOT_FOUND
            oneplugin[docutil.INFO_PLUGIN_FOLDER] = plugitem
            oneplugin[PLUGIN_FILES]=get_list_and_info_of_plugin_files(f"{files}/{plugitem}", ucproduct)
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

    # velocity plug-in information is actually available in the velocity-plug-in index
    return {
        "UCB": get_list_of_all_names(UCB_Docs, UCB_Files, "UCB"), # [], # 
        "UCD": get_list_of_all_names(UCD_Docs, UCD_Files, "UCD"), # [], #
        "UCR": get_list_of_all_names(UCR_Docs, UCR_Files, "UCR"), # [], #
        "UCV": get_list_of_all_names(UCV_Docs, UCV_Files, "UCV") #[] 
    }

def main():
    config = ucutil.get_config()

    adict = get_workfile(config)
    # logger1.debug(f"adict={adict}")

    with open("list.json", "w") as f:
        json.dump(adict,f, indent=4)
if __name__ == '__main__':
    main()
                