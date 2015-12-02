import json
import os
import random
import sys


def load_statistics(path):
    f = open(path)
    statistics = json.loads(f.read())
    f.close()

    return statistics


def get_upper_case_words_from_statistics(statistics):
    return filter(lambda word: word[0].isupper(), statistics[unicode('1')])


def weighted_choice(weights):
    totals = []
    running_total = 0.0

    for w in weights:
        running_total += w
        totals.append(running_total)

    rnd = random.random()
    for i in range(len(totals)):
        if rnd < totals[i]:
            return i

    return len(totals) - 1


def is_sentence_terminating(symbol):
    return symbol in ['.']


def is_roman_numeral(word):
    valid_roman_numerals = ["M", "D", "C", "L", "X", "V", "I", "(", ")"]
    return all(letter in valid_roman_numerals for letter in word)


def can_begin_sentence(word):
    if not word or not word[0].isupper():
        return False

    if filter(lambda letter: not letter.isalpha(), word):
        return False

    if is_roman_numeral(word):
        return False

    return True


def next_paragraph_length():
    AVERAGE_PARAGRAPH_LENGTH = 150
    AVERAGE_PARAGRAPH_LENGTH_DEVIATION = int(50 / 3)

    return random.gauss(AVERAGE_PARAGRAPH_LENGTH,
                        AVERAGE_PARAGRAPH_LENGTH_DEVIATION)


def generate_text(length, statistics, upper_case_words, min_sentence_length):
    text_words = []
    length_of_sentence = 0
    paragraph_length = 0
    cur_paragraph_length = 0
    i = 0
    while i < length or not is_sentence_terminating(text_words[-1][-1]):
        i += 1
        if not length_of_sentence:
            while paragraph_length < min_sentence_length:
                paragraph_length = next_paragraph_length()

            next_word = random.choice(upper_case_words)
            while not can_begin_sentence(next_word):
                next_word = random.choice(upper_case_words)

            text_words.append(next_word)
        else:
            if length_of_sentence == 1:
                if text_words[-1] not in statistics[u'1']:
                    text_words.append('.')
                else:
                    choices = statistics[u'1'][text_words[-1]]
                    random_position = weighted_choice([w for w, v in choices])
                    text_words.append(choices[random_position][1])
            else:
                jcode = unicode([text_words[-2], text_words[-1]])
                if jcode not in statistics[u'2']:
                    text_words.append('.')
                else:
                    choices = statistics[u'2'][jcode]
                    random_position = weighted_choice([w for w, v in choices])
                    text_words.append(choices[random_position][1])

        length_of_sentence += 1

        if is_sentence_terminating(text_words[-1]):
            if length_of_sentence <= min_sentence_length:
                i -= length_of_sentence
                while length_of_sentence:
                    text_words.pop()
                    length_of_sentence -= 1

            cur_paragraph_length += length_of_sentence
            length_of_sentence = 0

            if cur_paragraph_length > paragraph_length:
                cur_paragraph_length = 0
                text_words += '\n\t'

    return ' '.join(text_words).replace(' .', '.')


if __name__ == '__main__':
    length_of_text = int(sys.argv[2])
    minimal_sentence_length = int(sys.argv[3])

    path = sys.argv[1]
    json_path = os.path.join(path, 'json/statistics.json')

    statistics = load_statistics(json_path)
    upper_case_words = get_upper_case_words_from_statistics(statistics)
    generated_text = generate_text(length_of_text,
                                   statistics,
                                   upper_case_words,
                                   minimal_sentence_length)

    generated_text_path = os.path.join(path, 'generated_text')
    if not os.path.exists(generated_text_path):
        os.makedirs(generated_text_path)
    generated_text_path = os.path.join(generated_text_path,
                                       'generated_text.txt')

    with open(generated_text_path, 'w') as f:
        f.write(generated_text)
