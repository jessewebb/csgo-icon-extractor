# coding=utf-8
""" CS:GO Icon Extractor """


def parse_ids(ids_string):
    """
    Parse a list of icon IDs.
    :param ids_string: `swfextract` output string list of icon IDs (e.g. "1-3, 23, 99-123")
    :return: list of icon IDs as ints (e.g. [1, 2, 3, 23, 99, 100, ...])
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
