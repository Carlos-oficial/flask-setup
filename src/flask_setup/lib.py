import os, re


def mkdir_p(dir):
    if not os.path.exists(dir):
        os.mkdir(dir)


def mkdirs(*dirs):
    for dir in dirs:
        os.mkdir(dir)


def parse_and_replace(fin, path_out, expr2replace, replace_with):
    fout = open(path_out, "wt")
    fout.write(fin.replace(expr2replace, replace_with))
    fout.close()


def validate_app_name(name):
    return len(re.findall(r"[^A-Za-z0-9_\-\\]", name)) == 0
