# coding=utf-8
""" CS:GO Icon Extractor Tests """

from csgo_icon_extractor import parse_ids

import unittest


class ParseIdsTests(unittest.TestCase):
    """ Tests for csgo_icon_extractor.parse_ids() """

    def test_parses_list_of_single_id(self):
        self.assertEqual([0], parse_ids('0'))
        self.assertEqual([1], parse_ids('1'))
        self.assertEqual([23], parse_ids('23'))
        self.assertEqual([456], parse_ids('456'))
        self.assertEqual([7890], parse_ids('7890'))

    def test_parses_list_of_comma_separated_ids(self):
        self.assertEqual([1, 3], parse_ids('1, 3'))
        self.assertEqual([2, 456, 789], parse_ids('2, 456, 789'))

    def test_parses_list_of_id_ranges(self):
        self.assertEqual([1, 2, 3], parse_ids('1-3'))
        self.assertEqual([8, 9, 10, 99, 100, 101, 102], parse_ids('8-10, 99-102'))

    def test_parses_list_of_ids(self):
        self.assertEqual([0, 1, 2, 3, 4, 7, 8, 15, 16, 17, 35, 298, 299, 300, 301],
                         parse_ids('0-4, 7, 8, 15-17, 35, 298-301'))
