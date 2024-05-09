import os
import shutil
import logging
import sys
import json
from zipfile import ZipFile
import xmltodict
import zipfile
import pathlib
import datetime
# import py7zr
# import multivolumefile
from datetime import datetime
import subprocess


#sys.path.append('/Users/ozzy/RnD/Source/PLUGINS/urbancode-plugins-index/src/helper')
from helper import uc_docs_utilities as docutil 
from helper import uc_plugin_utilities as ucutil

standard_plugin_indicator = "info.xml"
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
    # logger1.debug (f"infoxml.version={version}")

    return semver, version, sort_version

def get_integration_type(doc):

    # try integrationType found in manfest.xml
    integration_type = integration_type = doc.get("pluginInfo", {}).get("integrationType", "")
    logger1.debug (f"integration_type={integration_type}")
    # try integrationType found in standard_plugin_indicator
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

def get_content_from_file(file, zf, target_dir):
    doc = {"pluginInfo": {'tool-description': "ERROR FILE DAMAGED"}}
    logger1.debug(f"accessing {file} from target_dir = {target_dir}")
    if (target_dir == ""):
        try:
            xfile=zf.read(file)
        except zipfile.BadZipFile as ex:
            logger1.error(f"ERROR FILE DAMAGED={file}")
            return doc
    else:
        with open(f"{target_dir}/{file}") as readfile:
            xfile=readfile.read()
    
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
        if (target_dir == ""): xfile=xfile.replace(b"'", b"") #replace(b"{", b"#curlybrace-open").replace(b"}", b"#curlybrace-close").
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

def get_info_from_jenkins_plugin(zf, file_info, target_dir):
    logger1.debug(f"file_list of hpi={zf.infolist()}")
    semver = "0.0"
    filename = "META-INF/MANIFEST.MF"
    doc = get_content_from_file(filename, zf, target_dir)
    logger1.debug (f" hpi content MANIFEST.MF = {doc}")
    semver=doc.get("Plugin-Version", "0.0")
    logger1.debug (f"semver={semver}")

    file_info_datetime = get_release_date(zf, filename, target_dir)
                
    logger1.debug(f"zipfileinfodatetimestring={file_info_datetime.strftime('%Y.%m.%d %H:%M')}")
    file_info[docutil.RELEASE_DATE]=file_info_datetime.strftime('%Y.%m.%d %H:%M')

    file_info[docutil.RELEASE_SEMVER], file_info[docutil.RELEASE_VERSION], file_info[SORT_VERSION] = get_semver_and_version(semver)

def is_standard_plugin(file_with_path, target_dir) -> bool:
    logger1.debug(f"file_with_path={file_with_path} - target_dir={target_dir}")
    standard_plugin = False

    if (target_dir == ""):
        with ZipFile(file_with_path, 'r') as zf:
            for file in zf.infolist():
                logger1.debug(f"file={file}")
                if file.filename == standard_plugin_indicator: 
                    standard_plugin = True
                    break
    else:
        if (standard_plugin_indicator in os.listdir(target_dir)):
            logger1.debug(f"{standard_plugin_indicator} found in {target_dir} -> standard plugin!")
            standard_plugin = True
       
    return standard_plugin

def get_info_from_standard_plugin(zf, file_info, target_dir):
    logger1.debug(f"target_dir={target_dir}")
    file_name= standard_plugin_indicator 
    get_info_from_infoxml(zf, file_name, file_info, target_dir)
    file_name= "manifest.xml"
    get_info_from_manifestxml(zf, file_name, file_info, target_dir)
    return 


def get_info_from_manifestxml(zf, file_name, file_info, target_dir):
    if (target_dir == ""):
        # check if manifest file is in zip
        listoffiles = zf.namelist()
        if (file_name not in listoffiles):
            return
    else:
        if not os.path.isfile(f"{target_dir}/{file_name}"):
            logger1.debug(f"{file_name} does not exist in {target_dir}")
            return
        
    doc = get_content_from_file(file_name, zf, target_dir)

    file_info[docutil.PLUGIN_SPECIFICATION_TYPE] = get_integration_type(doc)

    file_info[docutil.PLUGIN_SPECIFICATION_CATEGORIES] = get_categories(doc)
    return

def get_info_from_infoxml(zf, file_name, file_info, target_dir):
    logger1.debug(f"target_dir={target_dir} - file_name={file_name}")
    doc = get_content_from_file(file_name, zf, target_dir)

    file_info_datetime = get_release_date(zf, file_name, target_dir)
                
    logger1.debug(f"zipfileinfodatetimestring={file_info_datetime.strftime('%Y.%m.%d %H:%M')}")
    file_info[docutil.RELEASE_DATE]=file_info_datetime.strftime('%Y.%m.%d %H:%M')
                
    file_info[docutil.INFO_DESCRIPTION] = get_tool_description(doc, file_info[docutil.INFO_DESCRIPTION])

    semver=doc.get("pluginInfo", {}).get("release-version", "0.0")
    logger1.debug (f"semver={semver}")
    file_info[docutil.RELEASE_SEMVER], file_info[docutil.RELEASE_VERSION], file_info[SORT_VERSION] = get_semver_and_version(semver)

    file_info[docutil.PLUGIN_SPECIFICATION_TYPE] = get_integration_type(doc)

    # release notes
    file_info[docutil.RELEASE_NOTES] = get_release_notes(doc, file_info[docutil.RELEASE_SEMVER])
    return

def get_release_date(zf, filename, target_dir):
    release_date=""
    if (target_dir == ""):
        zipfileinfo=zf.getinfo(filename).date_time
        release_date = datetime(*zipfileinfo)
    else:
        release_date=datetime.fromtimestamp(os.path.getmtime(f"{target_dir}/{filename}"))
    logger1.debug(f"release_date={release_date}")
    return release_date

def get_velocity_file_info(file, file_info, pluginnamefolder, all_ucv_index_infos):
    # logger1.debug(f"velocity file={file} - file_info={file_info}")
    # fix the name "pluginnamefolder-" to "pluginnamefolder:"
    if f"{pluginnamefolder}-" in file:
        # replace the above with different text
        temp = file.replace(f"{pluginnamefolder}-", f"{pluginnamefolder}:")
        file = temp
        # logger1.info(f"updated file = {file}")
    if f"{pluginnamefolder}." in file:
        # replace the above with different text
        temp = file.replace(f"{pluginnamefolder}.", f"{pluginnamefolder}:")
        file = temp
        # logger1.info(f"updated file = {file}")

    splitted = file.split(".tar")
    logger1.debug(f"velocity splitted={splitted}")

    for plugin in all_ucv_index_infos:
       # logger1.debug(f"plugin={plugin}")
        for item in plugin["PLUGIN_FILES"]:
           # logger1.debug(f"item={item}")
            if splitted[0] in item["image"]:
                logger1.info(f"found={splitted[0]}")
                file_info[docutil.RELEASE_VERSION]=item[docutil.RELEASE_VERSION]
                file_info[docutil.RELEASE_SEMVER]=item[docutil.RELEASE_SEMVER]
                file_info[docutil.RELEASE_DATE]=item[docutil.RELEASE_DATE]
                file_info[docutil.RELEASE_NOTES]=item[docutil.RELEASE_NOTES]
                file_info[SORT_VERSION]=item[SORT_VERSION]
                file_info[docutil.RELEASE_IMAGE]=item[docutil.RELEASE_IMAGE]
                file_info[docutil.RELEASE_SUPPORTS]=item.get(docutil.RELEASE_SUPPORTS, "")
                logger1.info(f"file_info={file_info}")
                return

def unzip_file(file_with_path):
    config = ucutil.get_config()
    target_directory = config[ucutil.ZIP_TEMP_DIR]
    logger1.debug(f"7z x {file_with_path} -o{target_directory}")
    # first remove everything from target directory
    shutil.rmtree(target_directory)
    os.mkdir(target_directory)
    # Run 7zip command to extract multi-file 7zip archive
    try:
        subprocess.run(['7z', 'x', file_with_path, f'-o{target_directory}'])
    except:
        logger1.error(f"could not extract file={file_with_path}")
        return ""
    # if "FileUtils-43.752843.zip" in file_with_path:
    #     allfiles=os.listdir(target_directory)
    #     logger1.debug (f"DEBUG {target_directory}- {allfiles}")
    #     os._exit(1)
    return target_directory

def get_info_from_zip_file(plugin_path, file, file_info, ucproduct, pluginnamefolder, all_ucv_index_infos = []):
    file_with_path = f"{plugin_path}/{file}"
    logger1.info(f"file_with_path={file_with_path}")
    
    file_info[docutil.RELEASE_FILE]=file

    if ucproduct == "UCV": 
        # search for file pattern in all_ucv_index_infos and add data to file_info
        get_velocity_file_info(file, file_info, pluginnamefolder, all_ucv_index_infos)
        logger1.info(f"file_info after get velocity file info={file_info}")
        return
    
    if ((pluginnamefolder in ("AgentScript", "PHPCLI")) or ("SampleApplicationDeployments" in file_with_path) or ("db2-application-deployment-template-package" in file_with_path.lower())):
        logger1.warn(f"This is not a plug-in {pluginnamefolder}/{file}")
        file_info[docutil.RELEASE_FILE]=file
        file_info[docutil.INFO_DESCRIPTION]="NOT PLUGIN FILE"
        return

    ## special treatment for sample application
    if ("CreateCollectiveSampleApp.zip" in file_with_path):
        logger1.error("CreateCollectiveSample.zip handling needs to be implemented")
        file_info[docutil.RELEASE_FILE]=file
        file_info[docutil.INFO_DESCRIPTION]="NOT PLUGIN FILE - is a Sample"
        return
    # if file extension is 00x then it is packed with 7zip -> extract and use extracted file for processing
    # TODO: implement handling of 7ziped files and multivolume 7zip files...
    # if .001 in file_with_path -> use 7zip to unzip but not deep unzip     
    if (".7z" in file_with_path):
    # if (file_with_path.endswith(('.7z', '.001'))):
        logger1.info(f"7z file found - {file_with_path}")
       # logger1.error(f"ucproduct={ucproduct} - filewithpath={file_with_path} - plugin_path={plugin_path} - file={file} - file_info={file_info} - pluginnamefolder={pluginnamefolder}")
 
        # need to extract using 7zip and then use new file name to get info...
        # file_with_path = extracted file with new path
        config = ucutil.get_config()
        import subprocess

        # Run 7zip command to extract multi-file 7zip archive
        subprocess.run(['7z', 'x', file_with_path, f'-o{config[ucutil.ZIP_TEMP_DIR]}'])

        return 

    # when not a zipfile return with info
    # version info is "" also an indicator
    file_info[docutil.RELEASE_FILE]=file
    if (not zipfile.is_zipfile(file_with_path)):
        file_info[docutil.INFO_DESCRIPTION]="NOT PLUGIN FILE"
        return

    with ZipFile(file_with_path, 'r') as zf:

        # check if file can be manipulated with zipfile module or needs to be extracted
        logger1.debug(f"checking if {file_with_path} can be read with zipfile module")
        target_directory = ""
        try:
            if (".hpi" in file_with_path): 
                file = "META-INF/MANIFEST.MF"
            else:
                file = standard_plugin_indicator
            xfile=zf.read(file) # VERY BAD functionality, if file is OK, but the file to read is not in the zip then it fails -> is_standard_plugin should check...
        except zipfile.BadZipFile as ex:
            logger1.warn(f"file is not good={file} try alternative method")
            target_directory = unzip_file(file_with_path)
            logger1.debug(f"output of unzip_file={target_directory}")
            if (target_directory == ""):
                file_info[docutil.INFO_DESCRIPTION]="ERROR FILE DAMAGED"
                logger1.error(f"ERROR file is damaged file={file_with_path}")
                return

        if (".hpi" in file_with_path):
            get_info_from_jenkins_plugin(zf, file_info, target_directory) # get_info_from_jenkins_plugin(plugin_path, file, file_info)
        elif is_standard_plugin(file_with_path, target_directory): 
            get_info_from_standard_plugin(zf, file_info, target_directory)

    logger1.debug(f"file_info={file_info}")
    #if ("FileUtils-43.752843.zip" in file_with_path): os._exit(1)
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

def get_list_and_info_of_plugin_files(plugin_path, ucproduct, pluginnamefolder, all_ucv_index_infos = [] ):
    logger1.debug(f"{plugin_path} - name={pluginnamefolder} - product={ucproduct}")
    files=[]
    for file in get_files_with_dirs(plugin_path): #get_files(plugin_path):
        # if zipfile extension is 002 or higher than it is zipped with 7zip and process only 001 
        file_extension = pathlib.Path(file).suffix
        # if file_extension in { ".002", ".003", ".004", ".005"}:
        #     # need to find a solution how to unpack .001 and use unzipped file for further processing.
        #     continue
        
        # do not add "._xxxx" type of files, are from mac os
        if (file.startswith("._")): continue

        file_info = get_extended_release_template()
        get_info_from_zip_file(plugin_path,file, file_info, ucproduct, pluginnamefolder , all_ucv_index_infos)
        logger1.info(f"file_info={file_info}")
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

def get_product_readme(productpath):
    product_readme= ""

    with open(f"{productpath}/README.md", "r") as textf:
        product_readme = textf.readlines()
    return product_readme

def get_plugin_description(pluginname, product_readme):
    logger1.debug(f"pluginname={pluginname}")
    plugin_description = ""
    plugin_desc_found = False
    for line in product_readme:
        if f"## {pluginname}" in line and not plugin_desc_found:
            plugin_desc_found = True
        elif f"## {pluginname}" in line or plugin_desc_found:
            if "---" in line: break # return plugin_description
            plugin_description += line

    # remove "\n at the beginning and the end"
    return plugin_description.strip()

def get_ucv_index_infos():
    all_ucv_index_infos=[]
    config = ucutil.get_config()
    ucv_list_of_plugins = f"{config[ucutil.UCV_PLUGIN_INDEX_ROOT]}/{config[ucutil.UCV_PLUGIN_INDEX_PLUGINS_FOLDER]}"
    ucv_plugin_dir_names=get_plugin_dir_names(ucv_list_of_plugins)

    for ucv_plugin in ucv_plugin_dir_names:
        oneplugin=docutil.get_info_template()
        with open (f"{ucv_list_of_plugins}/{ucv_plugin}/info.json", "r") as f:
            infojson = json.loads(f.read())
        with open (f"{ucv_list_of_plugins}/{ucv_plugin}/releases.json", "r") as f:
            releasesjson = json.loads(f.read())
        files=[]
        for file in releasesjson:
            file_info = get_extended_release_template()
            file_info[docutil.RELEASE_NOTES]=file.get("notes")
            datetime_obj=datetime.fromisoformat(file.get("date")[:-1])
            # logger1.debug(f"datetime_obj={datetime_obj}")
            file_info[docutil.RELEASE_DATE] = datetime_obj.strftime("%Y.%m.%d %H:%M")
            file_info[docutil.RELEASE_SEMVER], file_info[docutil.RELEASE_VERSION], file_info[SORT_VERSION]=get_semver_and_version(file.get("semver"))
            file_info[docutil.RELEASE_IMAGE] = file.get(docutil.RELEASE_IMAGE)
            file_info[docutil.RELEASE_SUPPORTS] = file.get(docutil.RELEASE_SUPPORTS, "")
            files.append(file_info)

        oneplugin[docutil.INFO_NAME] = infojson.get("name")
        oneplugin[docutil.INFO_DESCRIPTION] = infojson.get("description")
        oneplugin[docutil.INFO_PLUGIN_FOLDER] = ucv_plugin
        oneplugin[NEW_FOLDER_NAME]=str(ucv_plugin).lower()
        oneplugin[PLUGIN_FILES] = files
        all_ucv_index_infos.append(oneplugin)
    # logger1.info(f"all ucv index infos={all_ucv_index_infos}")
    with open(f"UCV-allindex.json", "w") as f:
        json.dump(all_ucv_index_infos,f, indent=4)
    return all_ucv_index_infos

dummyoverride = [{
        "name": "dummyname",
        "docs_folder": "dummyname",
        "overwrite_with": {
          "description": "xxxxx",
          "specification": {
            "categories": [],
            "type": ""
          },
          "author": {
            "name": "",
            "email": ""
          },
          "publish": False,
          "name": "newname",
          "NEW_FOLDER_NAME": "yyz2"
        }
      }]

def get_override_info(forproduct):
    with open ("Overwrite-list.json", "r") as f:
        infojson = json.loads(f.read())
    return infojson.get(forproduct, dummyoverride)

def get_plugin_folder_name_from_doc_folder_name(docfoldername, all_plugin_folder_names, ucproduct):
    lowercase_pluginfolder_list = [x.lower() for x in all_plugin_folder_names]
    lowercase_docfoldername = docfoldername.lower()
    pluginfoldername=""
    if lowercase_docfoldername in lowercase_pluginfolder_list:
        index = lowercase_pluginfolder_list.index(lowercase_docfoldername)
        pluginfoldername = all_plugin_folder_names[index]
    else:
        # check now the override file
        overrideinfo=get_override_info(ucproduct)
        logger1.debug(f"overrideinfo={overrideinfo}")
        for item in overrideinfo:
            logger1.debug(f"item={item}")
            item_docs_folder=item.get(docutil.INFO_DOCS_FOLDER, "")
            logger1.debug(f"item_docs_folder={item_docs_folder}")
            if item_docs_folder == docfoldername:
                overridewith=item.get("overwrite_with", {})
                pluginfoldername = overridewith.get(docutil.INFO_PLUGIN_FOLDER, "")
    return pluginfoldername

def build_list(docs, files, ucproduct):
    listofplugins=[]

    all_plugin_doc_dir_names=get_plugin_dir_names(docs)
    all_plugin_files_dir_name=get_plugin_dir_names(files)
    # all_ucv_index_infos=[]
    all_ucv_index_infos = get_ucv_index_infos() if ucproduct == "UCV" else []
    product_readme=get_product_readme(f"{docs}")
    # logger1.debug(f"product readme={product_readme}")

    # iterate first over doc folders
    for docitem in all_plugin_doc_dir_names:
        logger1.debug(f"docitem/doc-folder-name={docitem}")
        oneplugin=docutil.get_info_template()
        oneplugin[docutil.INFO_NAME] = docutil.get_title_from_file(f"{docs}/{docitem}/{README}")
        # need oneplugin[docutil.INFO_NAME] and the product README
        oneplugin[docutil.INFO_DESCRIPTION] = get_plugin_description (oneplugin[docutil.INFO_NAME], product_readme)
        oneplugin[docutil.INFO_DOCS_FOLDER] = docitem
        oneplugin[NEW_FOLDER_NAME]=str(docitem).lower()
        oneplugin[docutil.INFO_SOURCE_PROJECT] = docutil.get_source_repository_from_file(f"{docs}/{docitem}/{README}")
        oneplugin[docutil.INFO_PLUGIN_SPECIFICATION] = get_plugin_specification(f"{docs}/{docitem}", ucproduct)

        # check if docfoldername can be found in pluginfolder name
        plugin_folder_name = get_plugin_folder_name_from_doc_folder_name(docitem, all_plugin_files_dir_name, ucproduct)
        if plugin_folder_name == "":
            logger1.warning(f"docitem={docitem} NOT found in all plugin files dir name")
            logger1.debug(f"sourcepro={oneplugin[docutil.INFO_SOURCE_PROJECT]}")
            if oneplugin[docutil.INFO_SOURCE_PROJECT] == "":
                oneplugin[docutil.INFO_PLUGIN_FOLDER] = docutil.get_plugin_folder_from_readme(f"{docs}/{docitem}")
        else:
            logger1.debug(f"docitem={docitem} found in all plugin files dir name")
            oneplugin[docutil.INFO_PLUGIN_FOLDER] = plugin_folder_name
            oneplugin[PLUGIN_FILES]=get_list_and_info_of_plugin_files(f"{files}/{plugin_folder_name}", ucproduct, docitem , all_ucv_index_infos )
        
        oneplugin[docutil.INFO_DOC_FILES] = get_all_doc_files(f"{docs}/{docitem}")
        logger1.debug(f"oneplugin={oneplugin}")

        if (oneplugin[docutil.INFO_SOURCE_PROJECT] == "") and (oneplugin[docutil.INFO_PLUGIN_FOLDER] == "" ): oneplugin[docutil.PUBLISH]=False

        listofplugins.append(oneplugin)

    for plugitem in all_plugin_files_dir_name:
        if (plugitem.lower() not in (name.lower() for name in all_plugin_doc_dir_names)): # (plugitem not in all_plugin_doc_dir_names): # 
            oneplugin=docutil.get_info_template()
            oneplugin[docutil.INFO_NAME] = DOCS_NOT_FOUND
            oneplugin[docutil.INFO_PLUGIN_FOLDER] = plugitem
            oneplugin[PLUGIN_FILES]=get_list_and_info_of_plugin_files(f"{files}/{plugitem}",ucproduct, plugitem.lower(),all_ucv_index_infos )
            if (oneplugin[docutil.INFO_SOURCE_PROJECT] == "") and (oneplugin[docutil.INFO_PLUGIN_FOLDER] == "" ): oneplugin[docutil.PUBLISH]=False
            listofplugins.append(oneplugin)        
    return listofplugins

def get_workfile(config, product):
    product_Docs = f"{config[ucutil.PLUGIN_DOCS_ROOT]}/{config[ucutil.PLUGIN_DOCS_FOLDER]}/{product}"
    product_ref = f"{product}_{ucutil.UCx_PLUGIN_FILES_ROOT}"
    product_Files = f"{config[product_ref]}/{config[ucutil.UCX_PLUGIN_FILES_FOLDER]}"

    return {
        product: build_list(product_Docs, product_Files, product)
    }

def main():
    config = ucutil.get_config()

    for product in  ["UCD"]:                         # ["UCR", "UCV"]: #["UCB", "UCD", "UCR", "UCV"]:
        with open(f"{product}-list.json", "w") as f:
            adict = get_workfile(config, product)
            json.dump(adict,f, indent=4)

if __name__ == '__main__':
    main()
                