import html2text
import os
import re
import sys


def contains_bad_sentence_begin(line):
    start = 0
    while True:
        start = line.find('.', start)
        if start == -1:
            return False

        if start + 1 < len(line) and line[start + 1].islower():
            return True

        start += 1


def number_of_words(line):
    return len(line.split())


def clean_line(line):
    forbidden_chars = r'|/\%^&@'
    braces = '(){}'
    if line and line[0].isalpha():
        cleaned_line = line.strip()

        if any(c in cleaned_line for c in forbidden_chars):
            return None

        cleaned_line = re.sub(r'\[.*\]', '', cleaned_line)
        cleaned_line = re.sub('[{}]'.format(''.join(braces)), '', cleaned_line)

        cleaned_line = cleaned_line.replace('_', '')
        cleaned_line = cleaned_line.replace('**', '')

        if contains_bad_sentence_begin(cleaned_line):
            return None

        return cleaned_line
    else:
        return None


def clean_text(text):
    text_lines = text.split('\n')
    cleaned_lines = []
    for line in text_lines:
        cleaned_line = clean_line(line)
        if cleaned_line:
            cleaned_lines.append(cleaned_line)

    return '\n'.join(cleaned_lines)


def convert_html_to_text(filepath, output_filepath):
    file_head = os.path.dirname(filepath)
    file_name = os.path.basename(filepath)

    if not file_name.endswith(('.html')):
        return None
    else:
        file_name = file_name[:-len('.html')] + '.txt'

    html2text_converter = html2text.HTML2Text()
    html2text_converter.ignore_links = True

    current_file = open(filepath)
    current_file_html = current_file.read().decode('utf8')
    current_file_text = html2text_converter.handle(current_file_html)
    current_file.close()

    current_file_text = clean_text(current_file_text)

    current_file_output = open(os.path.join(output_filepath, file_name), 'w')
    current_file_output.write(current_file_text.encode('utf8'))
    current_file_output.close()


def list_files(path):
    all_files = []
    for path, subdirs, files in os.walk(path):
        for f in files:
            all_files.append(os.path.join(path, f))
    return all_files


def convert_files_from_html_to_txt(files_list, output_path):
    for f in files_list:
        convert_html_to_text(f, output_path)


if __name__ == '__main__':
    absolute_path = sys.argv[1]
    output_path = os.path.join(absolute_path, 'text')

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    files_list = list_files(absolute_path)

    convert_files_from_html_to_txt(files_list, output_path)
