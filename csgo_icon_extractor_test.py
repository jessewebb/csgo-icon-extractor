# coding=utf-8
""" CS:GO Icon Extractor Tests """

from csgo_icon_extractor import parse_ids, parse_output_line, parse_output

import os
import unittest


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
    """ Tests for csgo_icon_extractor.parse_output_line() """

    def test_simple_output(self):
        output = 'Objects in file iconlib.swf:{}'.format(os.linesep) +\
                 ' [-i] 1 Shape: ID(s) 3{}'.format(os.linesep)
        result = parse_output(output)
        self.assertEqual(1, len(result))
        self.assertEqual('-i', result[0].flag)
        self.assertEqual('Shape', result[0].object_type)
        self.assertEqual(1, result[0].count)
        self.assertEqual([3], result[0].ids)
