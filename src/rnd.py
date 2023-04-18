# title = "NOT FOUND"
# with open("/Users/ozzy/RnD/Source/PLUGINS/IBM-UCx-PLUGIN-DOCS/docs/ucb/Sonar/README.md", "r") as file:
#     for line in file:
#         if line.startswith("#"):
#             title = line.strip("#").strip()  # remove "#" and any additional whitespace
#             break

# print(title)

# import re

# with open('/Users/ozzy/RnD/Source/PLUGINS/IBM-UCx-PLUGIN-DOCS/docs/ucb/Sonar/README.md', 'r') as f:
#     text = f.read()

# # Extract the title marked with equal signs
# match = re.search(r'^([\w\s]+)\n=+$', text, re.MULTILINE)

# if match:
#     title = match.group(1)
#     print(title)
# else:
#     print('No title found.')

file_name='/Users/ozzy/RnD/Source/PLUGINS/IBM-UCx-PLUGIN-DOCS/docs/ucb/Sonar/README.md'
# with open(file_name) as myfile:
#     lines=myfile.readlines()[0:5] #put here the interval you want

title=""
# with open("/Users/ozzy/RnD/Source/PLUGINS/IBM-UCx-PLUGIN-DOCS/docs/ucb/logigear-testarchitect-2/README.md", "r") as file:
#     for line in file:
#         if "[Source project](" in line:
#             print ("found the line")
#             splitted = line.split("[Source project](")
#             title = splitted[1].strip()[:-1]
#             break

from os import walk
import os

# folder path
dir_path = '/Volumes/T7/PLUGINS/IBM-UCD-PLUGINS/files'

def get_files_with_dirs(path):
    for (dir_path, dir_names, file_names) in os.walk(path):
        if file_names:
            newpath=dir_path.replace(f"{path}/", "")
            print (f"newpath={newpath}")
            for file in file_names:
                yield f"{newpath}/{file}" if newpath else file
# list to store files name
res = []
# for (dir_path, dir_names, file_names) in walk(dir_path):
#     print (f"dir_path = {dir_path}")
#     print (f"dir_names = {dir_names}")
#     print (f"file_names = {file_names}")
#     print ("------------------")
for file in get_files_with_dirs(dir_path):
    print (f"file={file}")

print (title)