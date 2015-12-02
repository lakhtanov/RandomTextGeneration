import json
import operator
import os
import re
import string
import sys


def is_sentence_terminating(symbol):
    return symbol in ['.', '\n']


def add_statistics_from_file(filepath, statistics, statistics_depth):
    current_file = open(filepath)
    words = re.split('(\W)', current_file.read().decode('utf8'))
    current_file.close()

    words = filter(None, words)
    words = filter(lambda word:
                   word.isdigit() or
                   is_sentence_terminating(word) or
                   word.isalpha(),
                   words)
    words = filter(lambda word:
                   len(word) > 1 or
                   word in ['.', 'i', 'I'],
                   words)

    for i in range(statistics_depth, len(words)):
        word = words[i]
        prev = tuple(words[i - statistics_depth:i])
        if prev not in statistics:
            statistics[prev] = {}

        if word in statistics[prev]:
            statistics[prev][word] += 1
        else:
            statistics[prev][word] = 1


def calculate_statistics_for_directory(path, levels, number_of_texts):
    statistics = {}
    for i in range(1, levels + 1):
        statistics[i] = {}

    cnt_texts = 0
    for path, subdirs, files in os.walk(path):
        for f in files:
            filepath = os.path.join(path, f)
            for level in range(1, levels + 1):
                cnt_texts += 1
                if cnt_texts == number_of_texts:
                    break
                add_statistics_from_file(filepath, statistics[level], level)
            if cnt_texts == number_of_texts:
                break
        if cnt_texts == number_of_texts:
            break

    for level in range(1, levels + 1):
        for word in statistics[level]:
            statistics[level][word] = sorted(
                [(v, k) for k, v in statistics[level][word].iteritems()])
            stat_sum = sum([pair[0] for pair in statistics[level][word]]) * 1.0
            for i in range(len(statistics[level][word])):
                pair = statistics[level][word][i]
                statistics[level][word][i] = (pair[0] / stat_sum, pair[1],)
    return statistics


def make_statistics_jsonable(statistics):
    jsonable_statistics = {}

    for level in statistics:
        jsonable_statistics[unicode(level)] = {}
        for key in statistics[level]:
            if level > 1:
                key_code = map(unicode, key)
            else:
                key_code = key[0]

            jlevel = unicode(level)
            jcode = unicode(key_code)
            jsonable_statistics[jlevel][jcode] = statistics[level][key]

    return jsonable_statistics


if __name__ == '__main__':
    number_of_used_files = int(sys.argv[2])

    path = sys.argv[1]
    text_path = os.path.join(path, 'text')

    json_path = os.path.join(path, 'json')
    if not os.path.exists(json_path):
        os.makedirs(json_path)
    json_path = os.path.join(json_path, 'statistics.json')

    statistics = calculate_statistics_for_directory(
        text_path, 2, number_of_used_files)
    statistics = make_statistics_jsonable(statistics)

    json_dump = open(json_path, 'w')
    json_dump.write(json.JSONEncoder().encode(statistics))
    json_dump.close()
