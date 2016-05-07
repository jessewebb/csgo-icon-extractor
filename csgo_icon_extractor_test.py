# coding=utf-8
""" CS:GO Icon Extractor Tests """
import os
import subprocess
import unittest

import mock

from csgo_icon_extractor import parse_ids, parse_output_line, parse_output, run_extract_command, ExtractorError, \
    extract_object_set_details_list, ObjectSetDetails


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
        output = 'Objects in file iconlib.swf:{}'.format(os.linesep) +\
                 ' [-i] 224 Shapes: ID(s) 286, 288, 290, 292, 296, 298, 300, 302, 304, 306, 308, 310, 312, 314, 316, 318, 320, 322, 324, 326, 328, 330, 332, 334, 336, 338, 340, 342, 344, 346, 348, 350, 352, 354, 356, 358, 360, 362, 364, 366, 368, 372, 374, 376, 378, 380, 382, 384, 386, 388, 390, 392, 394, 396, 398, 400, 402, 404, 406, 408, 410, 412, 415, 417, 419, 421, 423, 425, 428, 430, 432, 434, 436, 438, 440, 442, 444, 446, 448, 451, 453, 455, 457, 462, 465, 468, 470, 552, 554, 556, 559, 561, 567, 569, 571, 573, 577, 580, 584, 588, 591, 594, 599, 601, 603, 606, 609, 612, 617, 620, 623, 626, 630, 633, 635, 636, 638, 640-663, 665-674, 678, 681, 683, 686, 688, 692, 694, 696, 699, 702, 705, 708, 710, 714, 716, 721, 724, 728, 732, 736, 740, 742, 747, 750, 764, 766, 768, 770, 772, 774, 776, 778, 780, 782, 784, 786, 788, 790, 792, 794, 800, 808, 810, 812, 814, 816, 818, 820, 822, 825, 827, 830, 831, 836, 839-842, 844, 845, 847-858, 860{}'.format(os.linesep) +\
                 ' [-i] 255 MovieClips: ID(s) 287, 289, 291, 293, 295, 297, 299, 301, 303, 305, 307, 309, 311, 313, 315, 317, 319, 321, 323, 325, 327, 329, 331, 333, 335, 337, 339, 341, 343, 345, 347, 349, 351, 353, 355, 357, 359, 361, 363, 365, 367, 369-371, 373, 375, 377, 379, 381, 383, 385, 387, 389, 391, 393, 395, 397, 399, 401, 403, 405, 407, 409, 411, 413, 416, 418, 420, 422, 424, 426, 427, 429, 431, 433, 435, 437, 439, 441, 443, 445, 447, 449, 450, 452, 454, 456, 458-460, 463, 466, 469, 471-473, 475, 477, 479, 481, 483, 485, 487, 489, 491, 493, 495, 497, 499, 501, 503, 505, 507, 509, 511, 513, 515, 517, 519, 521, 523, 525, 527, 529, 531, 533, 535, 537, 539, 541, 543, 545, 547, 549, 551, 553, 555, 557, 558, 560, 562, 564, 566, 568, 570, 572, 574, 576, 578, 581, 582, 585, 586, 589, 592, 595, 597, 600, 602, 604, 605, 607, 608, 610, 613, 615, 618, 621, 624, 627, 629, 631, 634, 639, 675, 676, 679, 682, 684, 687, 689, 691, 693, 695, 697, 700, 703, 706, 709, 711, 713, 715, 717, 719, 722, 725, 727, 729, 731, 733, 735, 737, 739, 741, 743, 745, 748, 751, 753, 755, 757, 759, 761, 763, 765, 767, 769, 771, 773, 775, 777, 779, 781, 783, 785, 787, 789, 791, 793, 795, 797, 799, 801, 803, 805, 807, 809, 811, 813, 815, 817, 819, 821, 823, 824, 826, 828, 829, 832, 834, 835, 843, 859, 861, 862{}'.format(os.linesep) +\
                 ' [-j] 134 JPEGs: ID(s) 1-4, 6-27, 65, 186-193, 195-254, 256-265, 267-273, 278-285, 414, 461, 464, 467, 611, 619, 622, 625, 677, 707, 720, 723, 746, 749{}'.format(os.linesep) +\
                 ' [-p] 177 PNGs: ID(s) 5, 28-64, 66-185, 194, 255, 266, 274-277, 587, 590, 593, 598, 616, 632, 637, 680, 685, 698, 701, 704{}'.format(os.linesep) +\
                 ' [-f] 1 Frame: ID(s) 0{}'.format(os.linesep) +\
                 '{}'.format(os.linesep)
        result = parse_output(output)
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
        mock_run_subprocess.assert_called_once_with(['swfextract', iconlib_file])

    @mock.patch('subprocess.check_output')
    def test_passes_along_command_args_to_extract_subprocess(self, mock_run_subprocess):
        iconlib_file = mock.Mock()
        command_args = '-a 1 -b 2'
        run_extract_command(iconlib_file, command_args.split())
        mock_run_subprocess.assert_called_once_with(['swfextract', iconlib_file, '-a', '1', '-b', '2'])

    @mock.patch('subprocess.check_output')
    def test_raises_extractor_error_when_running_extract_subprocess_fails(self, mock_run_subprocess):
        mock_run_subprocess.side_effect = subprocess.CalledProcessError(123, 'extract')
        iconlib_file = mock.Mock()
        with self.assertRaises(ExtractorError) as e:
            run_extract_command(iconlib_file)
        self.assertEqual("Command 'extract' returned non-zero exit status 123", e.exception.message)


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
