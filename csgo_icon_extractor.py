# coding=utf-8
""" CS:GO Icon Extractor """

import os
import re
import subprocess
import sys


EXTRACT_CMD = 'swfextract'


def parse_ids(ids_string):
    """
    Parse a list of icon object IDs.
    :param ids_string: extract command output string list of icon object IDs (e.g. `"1-3, 23, 99-123"`)
    :return: list of icon object IDs as ints (e.g. `[1, 2, 3, 23, 99, 100, ...]`)
    """
    ids = []
    for id_string in ids_string.split(', '):
        if '-' in id_string:
            ids_range = id_string.split('-')
            first = int(ids_range[0])
            last = int(ids_range[1])
            ids.extend(range(first, last + 1))
        else:
            ids.append(int(id_string))
    return ids


class ObjectSetDetails(object):
    """
    The metadata about a set of Icon objects of the same type available for extraction.
    """
    def __init__(self, flag=None, object_type=None, count=None, ids=None):
        self.flag = flag
        self.object_type = object_type
        self.count = count
        self.ids = ids


def parse_output_line(output_line):
    """
    Parse a line of output from the extract command.
    :param output_line: single line of extract command output (without any new-line characters)
    :return: an instance of `ObjectSetDetails` if metadata could be parsed, `None` otherwise
    """
    if 'ID(s)' not in output_line:
        return None
    (info, ids_string) = output_line.split(': ID(s) ')
    info_re = re.compile(r'^ \[(?P<flag>-\w+)\] (?P<count>\d+) (?P<object_type>\w+?)s?$')
    info_match = info_re.match(info)
    flag = info_match.group('flag')
    object_type = info_match.group('object_type')
    count = int(info_match.group('count'))
    ids = parse_ids(ids_string)
    return ObjectSetDetails(flag=flag, object_type=object_type, count=count, ids=ids)


def parse_output(output):
    """
    Parse the output from running the extract command.
    :param output: multi-line extract command output
    :return: list of `ObjectSetDetails`, one for each icon object type
    """
    output_lines = output.split(os.linesep)
    parsed_lines = [parse_output_line(line) for line in output_lines]
    return [line_details for line_details in parsed_lines if line_details is not None]


class ExtractorError(Exception):
    def __init__(self, message):
        super(ExtractorError, self).__init__()
        self.message = message


def run_extract_command(iconlib_file, *command_args):
    command = [EXTRACT_CMD, iconlib_file]
    if command_args:
        command.extend(*command_args)
    try:
        command_output = subprocess.check_output(command)
        return command_output
    except subprocess.CalledProcessError as e:
        raise ExtractorError(str(e)), None, sys.exc_info()[2]


def extract_object_set_details_list(iconlib_file):
    output = run_extract_command(iconlib_file)
    object_set_details_list = parse_output(output)
    return object_set_details_list


def get_object_set_details_for_object_type(object_set_details_list, object_type):
    return next((osd for osd in object_set_details_list if osd.object_type == object_type), None)


def extract_icon_set(iconlib_file, object_set_details, icon_file_ext, output_dir):
    for icon_id in object_set_details.ids:
        output_file = '{}{}{}.{}'.format(output_dir, os.path.sep, icon_id, icon_file_ext)
        command_args = '{} {} -o {}'.format(object_set_details.flag, icon_id, output_file)
        run_extract_command(iconlib_file, command_args.split())
