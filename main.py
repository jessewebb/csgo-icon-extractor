#!/usr/bin/env python3
# coding=utf-8

""" csgo-icon-extractor script """

import argparse
import csgo_icon_extractor


DEFAULT_ICONLIB = 'iconlib.swf'
DEFAULT_OUTPUT_DIR = 'csgo-icons'


def _parse_command_line_args():
    parser = argparse.ArgumentParser(description='Extracts the CS:GO icon images from the icon lib SWF file.')
    parser.add_argument('iconlib', nargs='?', default=DEFAULT_ICONLIB, help='the icon lib SWF file')
    parser.add_argument('outdir', nargs='?', default=DEFAULT_OUTPUT_DIR, help='the directory to extract the icons into')
    return parser.parse_args()


def main():
    print('Running csgo-icon-extractor (version 1.0.0) ...')
    args = _parse_command_line_args()
    iconlib_file = args.iconlib
    output_dir = args.outdir
    print('Using configuration: iconlib={}, outdir={}'.format(iconlib_file, output_dir))
    csgo_icon_extractor.verfiy_swt_tools_is_in_path()
    csgo_icon_extractor.create_output_directory(output_dir)
    object_set_details_list = csgo_icon_extractor.extract_object_set_details_list(iconlib_file)
    for object_set_details in object_set_details_list:
        if object_set_details.object_type in csgo_icon_extractor.SUPPORTED_ICON_TYPE_MAP:
            icon_file_ext = csgo_icon_extractor.SUPPORTED_ICON_TYPE_MAP[object_set_details.object_type]
            csgo_icon_extractor.extract_icon_set(iconlib_file, object_set_details, icon_file_ext, output_dir)
            print('Extracted {} {}(s)'.format(len(object_set_details.ids), object_set_details.object_type))
    print('Icon extraction compete!')


if __name__ == "__main__":
    main()
