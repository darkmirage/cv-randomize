   ______     __  ____                 _                 _
  / ___\ \   / / |  _ \ __ _ _ __   __| | ___  _ __ ___ (_)_______
 | |    \ \ / /  | |_) / _` | '_ \ / _` |/ _ \| '_ ` _ \| |_  / _ \
 | |___  \ V /   |  _ < (_| | | | | (_| | (_) | | | | | | |/ /  __/
  \____|  \_/    |_| \_\__,_|_| |_|\__,_|\___/|_| |_| |_|_/___\___|

Raven Jiang
raven@cs.stanford.edu

Windows Instruction
==============================================================================

1.  Install python-2.7.5.msi
2.  Install lxml-3.2.1.win32-py2.7.exe
3.  Place the cv folder in C:\ (optional)
4.  Press Win + R to open the Windows Run dialog, type "cmd" and press Enter
5.  Type "cd C:\cv" (assuming step 3) and press Enter
6.  Type "C:\Python27\python cvrand.py template\cv1.docx 10" and press Enter

Mac and Linux Instructions
==============================================================================

Python generally come preinstalled, so try opening Terminal and going to the
/cv folder and run "python cvrand.py template/cv1.docx". You may need to
install the lxml Python module using pip.

Command Parameters Explained
==============================================================================

C:\Python27\python cvrand.py template\cv1.docx 10
  This is an example of a command used to execute the program

C:\Python27\python
  Refers to the installed path of the Python interpreter

cvrand.py
  Refers to the CV Randomize script in the active folder

template\cv1.docx
  This is the location of the template document relative to the current folder

10
  This is the number of CVs to generate using the specified template. Defaults
  to 5 if not specified.

Templating System
==============================================================================

The script looks for tags enclosed by [] in the template document and replaces
them with random values to produce a CV. The source data for the random
generator are stored as JSON files in the /data folder.

###
# Simple
###

In the simplest case, a random tag representing a discrete random value with
no dependencies is defined through the following:

Sample tag:           [tag_name]
Corresponding JSON:   tag_name.json
Content of JSON:
["random value 1", "random value 2", "random value 3"]

###
# Group Dependency
###

A random tag can belong to a group such that all tags belonging to the same
group will be have dependent values. (e.g. for a given person name, we want to
always have the same email address)

Sample tags:          [person.name] [person.email]
Corresponding JSON:   person.json
Content of JSON:
[
  { "name": "John", "email": "john@mailcatch.com" },
  { "name": "Mary", "email": "mary@mailcatch.com" }
]

###
# Internal Subfield Randomization
###

The above definitions ensure that whenever "John" is used for the value of
[person.name], "john@mailcatch.com" must be the value for [person.email]
Furthermore, tags can be further randomized within a single group.

For Example:
[
  {
    "name": "John",
    "email": ["john@mailcatch.com", "john2@yahoo.com"]
  },
  {
    "name": "Mary",
    "email": "mary@mailcatch.com"
  }
]

The above example means that whenever [person.name] is "John", one of the two
email addresses belonging to him will be used for [person.email]. Refer to
person.json for an example of this. Note that whitespace and line breaks in
JSON files are mostly for readability and have no syntactic meaning.

###
# External Subfield Randomization
###

Sometimes the list of random values for a subfield is too long to include in
every single group. Instead of defining an array in the JSON file of the
group, we can provide a reference to an external file.

Content of Group JSON (person.json):
[
  { "name": "John", "email": "_emails_" },
  { "name": "Mary", "email": "mary@mailcatch.com" }
]

The underscore characters indicate that this is not an actual value but a
reference to an external file. Refer to education.json for an example of this.

Corresponding JSON:   person.emails.json
Content of JSON:
["john@mailcatch.com", "john2@yahoo.com"]