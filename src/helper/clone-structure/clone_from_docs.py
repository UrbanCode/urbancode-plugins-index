import os
import logging
import sys
import re

sys.path.append('../')
sys.path.append('/Users/ozzy/RnD/Source/PLUGINS/urbancode-plugins-index/src/helper/')
sys.path.append('/Users/ozzy/RnD/Source/PLUGINS/urbancode-plugins-index/src/helper/docs-helper')
import uc_plugin_utilities as ucutil
import uc_docs_utilities as docutil 


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
def create_dirs_and_move_images(in_src, dst):
   
    imagefiles = ('.gif', '.jpg', '.png', '.jpeg' , '.GIF', '.JPG', '.PNG', '.JPEG')

    # getting the absolute path of the source
    # directory
    src = os.path.abspath(in_src)
    logger1.info(f"Source: {src}")

    # making a variable having the index till which
    # src string has directory and a path separator
    src_prefix = len(src) + len(os.path.sep)
     
    # making the destination directory
    os.makedirs(dst, exist_ok=True)
    logger1.info(f"created: {dst}")
     
    # doing os walk in source directory
    for root, dirs, files in os.walk(src):
        logger1.info (f"root={root} - dirs={dirs}")

        if "media" in root: continue

        if any(y in x for x in files for y in imagefiles):
            logger1.info("images in the dir!!!!")
        list_of_images=[]
        for file in files:
            logger1.info(f"file={file}")
            if (file.endswith(imagefiles)):
                list_of_images.append(file)
                logger1.info("image file found")
                dirpath = os.path.join(dst, root[src_prefix:], "media")
                logger1.info(f"dirpath={dirpath}")

                sfile=os.path.join(root,file)
                logger1.info (f"sfile={sfile}")
                tfile=os.path.join(dirpath, file)
                logger1.info (f"tfile={tfile}")
                os.makedirs(dirpath, exist_ok=True)
                os.rename(sfile,tfile)
        if len(list_of_images) == 0: continue

        for file in files:
            if (file.endswith(".md")):
                logger1.info(f"markdownfile={file}")
                filename=dirpath = os.path.join(root, file)
                logger1.info(f"filename={filename}")
                with open(filename, "r") as in_file:
                    filedata = in_file.read()
                new_filedata = filedata
                # replace the ?resize=xxxxxxxxx part
                new_filedata = re.sub(r"\?resize=.*\)", ")", new_filedata)
                for imagefile in list_of_images:
                    logger1.info(f"imagefile={imagefile}")
                    new_filedata = new_filedata.replace(f"({imagefile})", f"(media/{imagefile})")

                if new_filedata == filedata: 
                    logger1.info("no changes in file")
                    continue

                with open(filename, "wt") as out_file:
                    out_file.write(new_filedata)

    return
 

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
        logger1.info (f"root={root} - dirs={dirs}")
        for dirname in dirs:
           
            # here dst has destination directory,
            # root[src_prefix:] gives us relative
            # path from source directory
            # and dirname has folder names
            #logger1.info(f"root/src_prefix={root[src_prefix:]} - dirname={dirname}")
            dirpath = os.path.join(dst, root[src_prefix:], dirname)
            #logger1.info(f"dirpath={dirpath}")
            # making the path which we made by
            # joining all of the above three
            os.makedirs(dirpath, exist_ok=True)
            
            # ignore product-root folder
            if (dirname not in ['UCD', 'UCV', 'UCB', 'UCR']): 
                origpath=os.path.join(root, dirname)
                logger1.info(f"origpath={origpath}")
                info_object=docutil.get_info(origpath)
                logger1.info(f"info_obect={info_object}")

            # if in a plugi directory 

 
# calling the above function
def main():
    config = ucutil.get_config()
    # create_dirs_and_move_images(f"{config[ucutil.PLUGIN_DOCS_ROOT]}/{config[ucutil.PLUGIN_DOCS_FOLDER]}",
    #                             f"{config[ucutil.PLUGIN_DOCS_ROOT]}/{config[ucutil.PLUGIN_DOCS_FOLDER]}")
    create_dirtree_without_files(f"{config[ucutil.PLUGIN_DOCS_ROOT]}/{config[ucutil.PLUGIN_DOCS_FOLDER]}",
                                 f"{config[ucutil.PLUGIN_DOCS_ROOT]}/{config[ucutil.PLUGIN_DOCS_FILES_FOLDER]}")
if __name__ == '__main__':
    main()
                