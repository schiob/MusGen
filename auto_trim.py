import os

lily_file_name = os.sys.argv[1]
output_name = os.sys.argv[2]
os.system("lilypond -dbackend=eps {}".format(lily_file_name))
os.system("convert -density 1000x1000 {}eps {}".format(lily_file_name[:-2], output_name))
os.system("rm {}-*".format(lily_file_name[:-3]))
os.system("rm {}.eps".format(lily_file_name[:-3]))
os.system("rm {}.pdf".format(lily_file_name[:-3]))
os.system("convert {0}.jpg -crop x7000 {0}.jpg".format(output_name[:-4]))
os.system("convert -trim {}-0.jpg {}".format(output_name[:-4], output_name))
os.system("rm {}-*".format(output_name[:-4]))

