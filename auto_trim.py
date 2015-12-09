"""This module takes 2 arguments, the source .ly file and the name of the output.jpg file.
It returns the converted jpg and put it in a dir named img
"""

import os

lily_file_name = os.sys.argv[1]
output_name = os.sys.argv[2]
os.system("lilypond -dbackend=eps {}".format(lily_file_name))
if '/' in lily_file_name:
    lily_file_name = lily_file_name[lily_file_name.index('/')+1:]
os.system("convert -density 1000x1000 {}eps {}".format(lily_file_name[:-2], output_name))
os.system("rm {}-*".format(lily_file_name[:-3]))
os.system("rm {}.eps".format(lily_file_name[:-3]))
os.system("rm {}.pdf".format(lily_file_name[:-3]))
os.system("convert {0}.jpg -crop x7000 {0}.jpg".format(output_name[:-4]))
os.system("convert -trim {}-0.jpg {}".format(output_name[:-4], output_name))
os.system("rm {}-*".format(output_name[:-4]))
if not os.path.isdir("img"):
    os.system("mkdir img")
os.system("mv {0} img/{0}".format(output_name))
