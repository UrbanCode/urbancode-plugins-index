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
with open("/Users/ozzy/RnD/Source/PLUGINS/IBM-UCx-PLUGIN-DOCS/docs/ucb/logigear-testarchitect-2/README.md", "r") as file:
    for line in file:
        if "[Source project](" in line:
            print ("found the line")
            splitted = line.split("[Source project](")
            title = splitted[1].strip()[:-1]
            break

print (title)