# -*- coding: utf-8 -*-
"""
Created on Sun Oct  2 12:56:12 2022

@author: Darshan Rathod

converts .ipynb to markdown file
"""


import re
import nbformat
from traitlets.config import Config
from nbconvert import HTMLExporter, MarkdownExporter
import os

parent_folder = r'.'
module_name = 'ddr_mfc'


# read the raw data
fp1 = os.path.join(parent_folder,'Readme.ipynb')
with open(fp1) as f1:
    l1 = f1.readlines()
    
# make the data in jupyter notebook format, nb1 here is dict object which contains all infor about jupyter notebook
s = ''
s = s.join(l1)
nb1 = nbformat.reads(s, as_version=4)

# this removes the input of cells marked with "remove=input" tag.
c = Config()
c.TagRemovePreprocessor.remove_input_tags = ("remove-input",)
c.TagRemovePreprocessor.enabled = True

# give this configuration to exporter
html_exporter = MarkdownExporter(config=c)
(body, resources) = html_exporter.from_notebook_node(nb1)

# body does not contain input of cells marked with the tags, and body is str object with markdown syntex.
# we can directly write this body into .md file. but inside body there are images tags, where we have to give proper
# path to the images.

# make folder to store images
imgfold = os.path.join(parent_folder,'README_files')
try:
    os.mkdir(imgfold)
except FileExistsError as e:
    pass

# store all the images in .png format
for i in resources['outputs']:
    img = resources['outputs'][i]
    imgpath = os.path.join(imgfold,i)
    
    # img is byte type object. Hence we will open the file with 'wb' permission. orlese the error of 'str object' will come.
    with open(imgpath,'wb') as f1:
        f1.write(img)
    
# change the image pointer in the markdown string (body). here we will point the image location to github library so that
# image can be loaded in pypi. becuase pypi needs url of the image.
# first we will search in the body where the images are, and then change its pointer.
# images in markdown are inserted using
# ![png](Output_0.png)
# here we will change the content inside bracket and give the github url of the image.

# first we will find the location of the strings and then we will replace in separate loop.
l_str = []
l_img_name = []
for m in re.finditer(r"!\[png\]",body):
    str1 = ''
    i1 = m.end()
    i2 = i1
    while str1!= ')':
        i2 = i2 + 1
        str1 = body[i2]
    str1 = body[m.start():i2] 
    iname1 = body[i1+1:i2]
    l_str.append(str1)
    l_img_name.append(iname1)

# replace the found strings
for str1,iname1 in zip(l_str,l_img_name):
    i1 = body.find(str1)
    rstr1 = r'![png](https://github.com/ddrathod121294/' + module_name + '/blob/base/README_files/' + iname1 +'?raw=true'
    body = body.replace(str1,rstr1)
    
# now we will write the body in README.md file
fp1 = os.path.join(parent_folder,'README.md')
with open(fp1,'w') as f1:
    f1.write(body)
    
#done