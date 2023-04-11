import os
import logging
import sys
import json

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

def get_plugin_dir_names(src):
    # getting the absolute path of the source
    # directory
    src = os.path.abspath(src)
    logger1.info(f"Source: {src}")

    # for root, dirs, files in os.walk(src):
    #     logger1.info (f"root={root} - dirs={dirs}")
    #     for dirname in dirs:
    #         logger1.info (f"dirname={dirname}")            
    list_subfolders_with_paths = [f.name for f in os.scandir(src) if f.is_dir()]
    # logger1.info (f"list_subfoldes={list_subfolders_with_paths}")
    return sorted(list_subfolders_with_paths)

def get_list_of_all_names(docs, files):
    listofplugins=[]

    all_plugin_doc_dir_names=get_plugin_dir_names(docs)
    all_plugin_files_dir_name=get_plugin_dir_names(files)

    # iterate first over doc folders

    for docitem in all_plugin_doc_dir_names:
        oneplugin=docutil.get_info_template()
        oneplugin[docutil.INFO_DOCS] = docitem
        if (docitem in all_plugin_files_dir_name):
            # oneplugin[docutil.INFO_NAME] = docitem
            oneplugin[docutil.INFO_PLUGIN_FOLDER] = docitem
        else:
            oneplugin[docutil.INFO_NAME] = "PLUGINS-NOT-FOUND"
        
        oneplugin[docutil.INFO_NAME] = docutil.get_title_from_file(f"{docs}/{docitem}/README.md")

        listofplugins.append(oneplugin)

    for plugitem in all_plugin_files_dir_name:
        if (plugitem not in all_plugin_doc_dir_names):
            oneplugin=docutil.get_info_template()
            oneplugin[docutil.INFO_NAME] = "DOCS-NOT-FOUND"
            oneplugin[docutil.INFO_PLUGIN_FOLDER] = plugitem
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
            "UCB" : get_list_of_all_names(UCB_Docs, UCB_Files),
            "UCD" : get_list_of_all_names(UCD_Docs, UCD_Files),
            "UCR" : get_list_of_all_names(UCR_Docs, UCR_Files),
            "UCV" : get_list_of_all_names(UCV_Docs, UCV_Files)
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
                