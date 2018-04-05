# coding=utf-8
""" CS:GO Icon Extractor Tests """
import os
import subprocess
import unittest

import mock

from csgo_icon_extractor import parse_ids, parse_output_line, parse_output, run_extract_command, ExtractorError, \
    extract_object_set_details_list, ObjectSetDetails, get_object_set_details_for_object_type, extract_icon_set, \
    create_output_directory


class ParseIdsTests(unittest.TestCase):
    """ Tests for csgo_icon_extractor.parse_ids() """

    def test_single_id(self):
        self.assertEqual([0], parse_ids('0'))
        self.assertEqual([1], parse_ids('1'))
        self.assertEqual([23], parse_ids('23'))
        self.assertEqual([456], parse_ids('456'))
        self.assertEqual([7890], parse_ids('7890'))

    def test_comma_separated_ids(self):
        self.assertEqual([1, 3], parse_ids('1, 3'))
        self.assertEqual([2, 456, 789], parse_ids('2, 456, 789'))

    def test_id_ranges(self):
        self.assertEqual([1, 2, 3], parse_ids('1-3'))
        self.assertEqual([8, 9, 10, 99, 100, 101, 102], parse_ids('8-10, 99-102'))

    def test_complex_list_of_ids(self):
        self.assertEqual([0, 1, 2, 3, 4, 7, 8, 15, 16, 17, 35, 298, 299, 300, 301],
                         parse_ids('0-4, 7, 8, 15-17, 35, 298-301'))


class ParseOutputLineTests(unittest.TestCase):
    """ Tests for csgo_icon_extractor.parse_output_line() """

    def test_single_id(self):
        output_line = ' [-f] 1 Frame: ID(s) 0'
        result = parse_output_line(output_line)
        self.assertEqual('-f', result.flag)
        self.assertEqual('Frame', result.object_type)
        self.assertEqual(1, result.count)
        self.assertEqual([0], result.ids)

    def test_list_of_ids(self):
        output_line = ' [-j] 12 JPEGs: ID(s) 4, 18-23, 695, 696, 703-705'
        result = parse_output_line(output_line)
        self.assertEqual('-j', result.flag)
        self.assertEqual('JPEG', result.object_type)
        self.assertEqual(12, result.count)
        self.assertEqual([4, 18, 19, 20, 21, 22, 23, 695, 696, 703, 704, 705], result.ids)

    def test_header_line(self):
        output_line = 'Objects in file iconlib.swf:'
        result = parse_output_line(output_line)
        self.assertIsNone(result)


class ParseOutputTests(unittest.TestCase):
    """ Tests for csgo_icon_extractor.parse_output() """

    def test_simple_output(self):
        output = 'Objects in file iconlib.swf:{}'.format(os.linesep) +\
                 ' [-i] 1 Shape: ID(s) 3{}'.format(os.linesep)
        result = parse_output(output)
        self.assertEqual(1, len(result))
        self.assertEqual('-i', result[0].flag)
        self.assertEqual('Shape', result[0].object_type)
        self.assertEqual(1, result[0].count)
        self.assertEqual([3], result[0].ids)

    def test_complex_output(self):
        output = 'Objects in file iconlib.swf:{}'.format(os.linesep) +\
                 ' [-p] 10 PNGs: ID(s) 5, 18-20, 99, 100, 110-113{}'.format(os.linesep) +\
                 ' [-j] 4 JPEGs: ID(s) 8, 21, 23, 98{}'.format(os.linesep) +\
                 '{}'.format(os.linesep)
        result = parse_output(output)
        self.assertEqual(2, len(result))
        self.assertEqual('-p', result[0].flag)
        self.assertEqual('PNG', result[0].object_type)
        self.assertEqual(10, result[0].count)
        self.assertEqual([5, 18, 19, 20, 99, 100, 110, 111, 112, 113], result[0].ids)
        self.assertEqual('-j', result[1].flag)
        self.assertEqual('JPEG', result[1].object_type)
        self.assertEqual(4, result[1].count)
        self.assertEqual([8, 21, 23, 98], result[1].ids)

    def test_real_output(self):
        real_output_filename = 'swfextract-real-output.txt'
        with open(real_output_filename) as real_output_file:
            real_output = real_output_file.read()
        result = parse_output(real_output)
        self.assertEqual(5, len(result))
        # Shapes
        self.assertEqual('-i', result[0].flag)
        self.assertEqual('Shape', result[0].object_type)
        self.assertEqual(224, result[0].count)
        self.assertEqual(224, len(result[0].ids))
        # MovieClips
        self.assertEqual('-i', result[1].flag)
        self.assertEqual('MovieClip', result[1].object_type)
        self.assertEqual(255, result[1].count)
        self.assertEqual(255, len(result[1].ids))
        # JPEGs
        self.assertEqual('-j', result[2].flag)
        self.assertEqual('JPEG', result[2].object_type)
        self.assertEqual(134, result[2].count)
        self.assertEqual(134, len(result[2].ids))
        # PNGs
        self.assertEqual('-p', result[3].flag)
        self.assertEqual('PNG', result[3].object_type)
        self.assertEqual(177, result[3].count)
        self.assertEqual(177, len(result[3].ids))
        # Frames
        self.assertEqual('-f', result[4].flag)
        self.assertEqual('Frame', result[4].object_type)
        self.assertEqual(1, result[4].count)
        self.assertEqual([0], result[4].ids)


class RunExtractCommandTests(unittest.TestCase):
    """ Tests for csgo_icon_extractor.run_extract_command() """

    @mock.patch('subprocess.check_output')
    def test_returns_command_output(self, mock_run_subprocess):
        command_output = 'fake output'
        mock_run_subprocess.return_value = command_output
        iconlib_file = mock.Mock()
        result = run_extract_command(iconlib_file)
        self.assertEqual(command_output, result)

    @mock.patch('subprocess.check_output')
    def test_runs_extract_subprocess_on_iconlib_file(self, mock_run_subprocess):
        iconlib_file = mock.Mock()
        run_extract_command(iconlib_file)
        mock_run_subprocess.assert_called_once_with(['swfextract', iconlib_file], universal_newlines=True)

    @mock.patch('subprocess.check_output')
    def test_passes_along_command_args_to_extract_subprocess(self, mock_run_subprocess):
        iconlib_file = mock.Mock()
        command_args = '-a 1 -b 2'
        run_extract_command(iconlib_file, command_args.split())
        mock_run_subprocess.assert_called_once_with(['swfextract', iconlib_file, '-a', '1', '-b', '2'],
                                                    universal_newlines=True)

    @mock.patch('subprocess.check_output')
    def test_raises_extractor_error_when_running_extract_subprocess_fails(self, mock_run_subprocess):
        mock_run_subprocess.side_effect = subprocess.CalledProcessError(123, 'extract')
        iconlib_file = mock.Mock()
        with self.assertRaises(ExtractorError) as e:
            run_extract_command(iconlib_file)
        self.assertEqual("command 'extract' returned non-zero exit code 123", e.exception.message)


class ExtractObjectSetDetailsListTests(unittest.TestCase):
    """ Tests for csgo_icon_extractor.extract_object_set_details_list() """

    @mock.patch('csgo_icon_extractor.parse_output', return_value=[ObjectSetDetails()])
    @mock.patch('csgo_icon_extractor.run_extract_command')
    def test_runs_extract_command_and_parses_command_output(self, mock_run_extract_cmd, mock_parse_output):
        command_output = 'fake extract command output'
        mock_run_extract_cmd.return_value = command_output
        iconlib_file = mock.Mock()
        extract_object_set_details_list(iconlib_file)
        mock_parse_output.assert_called_once_with(command_output)

    @mock.patch('csgo_icon_extractor.parse_output')
    @mock.patch('csgo_icon_extractor.run_extract_command', mock.Mock(return_value='output'))
    def test_returns_list_of_object_set_details_from_the_parsed_output(self, mock_parse_output):
        parse_output_result = [ObjectSetDetails(flag='-a', object_type='Foo', count=3, ids=[1, 2, 3]),
                               ObjectSetDetails(flag='-b', object_type='Bar', count=1, ids=[4])]
        mock_parse_output.return_value = parse_output_result
        iconlib_file = mock.Mock()
        result = extract_object_set_details_list(iconlib_file)
        self.assertEqual(parse_output_result, result)


class GetObjectSetDetailsForObjectTypeTests(unittest.TestCase):
    """ Tests for csgo_icon_extractor.get_object_set_details_for_object_type() """

    def test_returns_the_object_set_details_matching_given_object_type_when_its_first_in_the_list(self):
        object_set_details1 = ObjectSetDetails(object_type='Type1')
        object_set_details2 = ObjectSetDetails(object_type='Type2')
        object_set_details_list = [object_set_details1, object_set_details2]
        result = get_object_set_details_for_object_type(object_set_details_list, 'Type1')
        self.assertEqual(object_set_details1, result)

    def test_returns_the_object_set_details_matching_given_object_type_when_its_in_the_middle_of_the_list(self):
        object_set_details1 = ObjectSetDetails(object_type='type one')
        object_set_details2 = ObjectSetDetails(object_type='type two')
        object_set_details3 = ObjectSetDetails(object_type='type three')
        object_set_details_list = [object_set_details1, object_set_details2, object_set_details3]
        result = get_object_set_details_for_object_type(object_set_details_list, 'type two')
        self.assertEqual(object_set_details2, result)

    def test_returns_the_object_set_details_matching_given_object_type_when_its_last_in_the_list(self):
        object_set_details1 = ObjectSetDetails(object_type='foo')
        object_set_details2 = ObjectSetDetails(object_type='bar')
        object_set_details3 = ObjectSetDetails(object_type='baz')
        object_set_details4 = ObjectSetDetails(object_type='bing')
        object_set_details_list = [object_set_details1, object_set_details2, object_set_details3, object_set_details4]
        result = get_object_set_details_for_object_type(object_set_details_list, 'bing')
        self.assertEqual(object_set_details4, result)

    def test_returns_none_when_object_set_details_dont_exist_for_given_object_type(self):
        object_set_details1 = ObjectSetDetails(object_type='PNG')
        object_set_details2 = ObjectSetDetails(object_type='Shape')
        object_set_details_list = [object_set_details1, object_set_details2]
        result = get_object_set_details_for_object_type(object_set_details_list, 'JPEG')
        self.assertIsNone(result)


class ExtractIconSetTests(unittest.TestCase):
    """ Tests for csgo_icon_extractor.extract_icon_set() """

    @mock.patch('csgo_icon_extractor.run_extract_command')
    def test_runs_extract_command_with_expected_arguments(self, mock_run_extract_cmd):
        iconlib_file = mock.Mock()
        object_set_details = ObjectSetDetails(flag='-t', ids=[123])
        icon_file_ext = 'ext'
        output_dir = 'icons_output'
        expected_extract_cmd_args = '-t 123 -o icons_output{}123.ext'.format(os.path.sep)
        extract_icon_set(iconlib_file, object_set_details, icon_file_ext, output_dir)
        mock_run_extract_cmd.assert_called_once_with(iconlib_file, expected_extract_cmd_args.split())

    @mock.patch('csgo_icon_extractor.run_extract_command')
    def test_runs_extract_command_for_each_icon_id_in_set_details(self, mock_run_extract_cmd):
        ids = [1, 2, 3, 4]
        extract_icon_set(mock.Mock(), ObjectSetDetails(ids=ids), 'ext', 'out')
        self.assertEqual(len(ids), mock_run_extract_cmd.call_count)


class CreateOutputDirectoryTests(unittest.TestCase):
    """ Tests for csgo_icon_extractor.create_output_directory() """

    @mock.patch('os.makedirs')
    @mock.patch('os.path.exists')
    def test_makes_the_output_dir_when_it_doesnt_exist(self, mock_path_exists, mock_make_dirs):
        mock_path_exists.return_value = False
        output_dir = 'output_dir'
        create_output_directory(output_dir)
        mock_make_dirs.assert_called_once_with(output_dir)

    @mock.patch('os.makedirs')
    @mock.patch('os.path.isdir')
    @mock.patch('os.path.exists')
    def test_does_nothing_when_the_output_dir_already_exists(self, mock_path_exists, mock_path_is_dir, mock_make_dirs):
        mock_path_exists.return_value = True
        mock_path_is_dir.return_value = True
        create_output_directory('output_dir')
        mock_make_dirs.assert_not_called()

    @mock.patch('os.makedirs')
    @mock.patch('os.path.isdir')
    @mock.patch('os.path.exists')
    def test_raises_extractor_error_when_the_output_dir_already_exists_but_it_is_not_a_directory(
            self, mock_path_exists, mock_path_is_dir, mock_make_dirs):
        mock_path_exists.return_value = True
        mock_path_is_dir.return_value = False
        with self.assertRaises(ExtractorError) as e:
            create_output_directory('not-a-dir')
        self.assertEqual("output_dir 'not-a-dir' already exists but is not a directory", e.exception.message)
        mock_make_dirs.assert_not_called()
