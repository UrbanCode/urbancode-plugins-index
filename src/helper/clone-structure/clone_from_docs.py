import os
import logging
import sys
sys.path.append('../')
sys.path.append('/Users/ozzy/RnD/Source/PLUGINS/urbancode-plugins-index/src/helper/')
import uc_plugin_utilities as ucutil

script_name = "clone_from_docs"

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

# saw this example here: https://www.geeksforgeeks.org/python-copy-directory-structure-without-files/


# defining a function for the task
def create_dirtree_without_files(src, dst):
   
    # getting the absolute path of the source
    # directory
    src = os.path.abspath(src)
    logger1.info(f"Source: {src}")

    # making a variable having the index till which
    # src string has directory and a path separator
    src_prefix = len(src) + len(os.path.sep)
     
    # making the destination directory
    os.makedirs(dst, exist_ok=True)
    logger1.info(f"created: {dst}")
     
    # doing os walk in source directory
    for root, dirs, files in os.walk(src):
        for dirname in dirs:
           
            # here dst has destination directory,
            # root[src_prefix:] gives us relative
            # path from source directory
            # and dirname has folder names
            dirpath = os.path.join(dst, root[src_prefix:], dirname)
            logger1.info(f"dirpath={dirpath}")
            # making the path which we made by
            # joining all of the above three
            os.makedirs(dirpath, exist_ok=True)
 
# calling the above function
def main():
    config = ucutil.get_config()
    create_dirtree_without_files(f"{config[ucutil.PLUGIN_DOCS_ROOT]}/{config[ucutil.PLUGIN_DOCS_FOLDER]}",
                                 f"{config[ucutil.PLUGIN_DOCS_ROOT]}/{config[ucutil.PLUGIN_DOCS_FILES_FOLDER]}")
if __name__ == '__main__':
    main()
                