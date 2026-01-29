#!/usr/bin/env python3
'''
NAME:    lf_help_to_cookbook_convert.py

PURPOSE:    read in help text file and convert for cookbook

USAGE:    lf_help_to_cookbook_convert.py --file <file>

EXAMPLE:    lf_help_to_cookbook_convert.py --file <file>

SCRIPT_CLASSIFICATION : Tool

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2025 Candela Technologies Inc


INCLUDE_IN_README

'''
import argparse


class file_convert():
    def __init__(self,
                 _file=''):
        self.file = _file
        self.file2 = "cookbook_{}".format(_file)

    # Helper methods
    def json_file(self):
        file_fd = open(self.file, 'r')
        file2_fd = open(self.file2, 'w+')
        file2_fd.write('{\n')
        file2_fd.write('"text": [ "<P><pre style=\'width: 700px; height: 400px; font-size: 8pt; overflow: scroll\'\\\\","class=\'scroll\'>\\\\",**{}**\\\\",'.format(self.file))
        for line in file_fd:
            line = line.replace('"', '&quot;').replace('\n', '')
            # to avoid --raw_line \"  issues the \" it creates a \& which the reader does not like
            # original line:  line = line.replace('\&', '\\\&')  # noqa: W605 W605
            line = line.replace(r'&', r'\&')
            line = '"<br>' + line + '\\\\",'

            file2_fd.write('{}\n'.format(line))
        file2_fd.write('"</pre>"]\n')
        file2_fd.write('},')
        file_fd.close()
        file2_fd.close()


def main():

    parser = argparse.ArgumentParser(
        prog='lf_help_to_cookbook_convert.py',
        formatter_class=argparse.RawTextHelpFormatter,
        epilog='''\
        lf_help_to_cookbook_convert.py converts script help output to js cookbook type output
            ''',
        description=r'''
NAME:    lf_help_to_cookbook_convert.py

PURPOSE:    read in help text file and convert for cookbook

USAGE:    lf_help_to_cookbook_convert.py --file <file>

EXAMPLE:    lf_help_to_cookbook_convert.py --file <file>

SCRIPT_CLASSIFICATION : Tool

LICENSE:
    Free to distribute and modify. LANforge systems must be licensed.
    Copyright 2025 Candela Technologies Inc


INCLUDE_IN_README

        ''')
    parser.add_argument('--file', help='--file file.json', required=True)

    args = parser.parse_args()

    __file = args.file

    convert = file_convert(_file=__file)
    convert.json_file()


if __name__ == '__main__':
    main()
