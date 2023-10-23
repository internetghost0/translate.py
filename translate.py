#!/bin/env python3
import requests
import re
import sys
from base64 import b64decode, b64encode
import os
def clear_console():
    if os.name == 'posix': # linux, macos, etc
        os.system('clear') 
    else:
        os.system('cls')	# windows


def parse_translation(page):
    pattern = r'<div class="t_inline_en">(.*?)</div>' # en -> ru
    if('t_inline_en' not in page):
        pattern = r'<p class="t_inline">(.*?)</p>' # ru -> en
    matchObj = re.search(pattern,page, re.M|re.I)
    if matchObj:
        return matchObj.group(1)
    else:
        pattern = r'<div class="light_tr"> (.*?) </div>'
        matchObj = re.search(pattern,page, re.M|re.I)
        if matchObj:
            return matchObj.group(1)
        else:
            raise Exception('cannot parse a page')

def parse_possible_variants(page):
    pattern = 'class="possible_variant">(.*?)</a'
    return re.findall(pattern, page)

def parse_similar_words(page):
    pattern = '<div class="block similar_words">(.*?)</div>'
    matchObj = re.search(pattern, page, re.M|re.I)
    if not matchObj: return None
    res = []
    tmp = matchObj.group(1)
    while True:
        e = tmp.find('</a>')
        if (e == -1): break
        b = tmp[:e].rfind('>')
        res.append(tmp[b+1:e])
        tmp = tmp[e+3:]
    return res


def translate(word, get_func=requests.get):
    url_base = 'https://wooordhunt.ru/word/'
    err_not_found = 'word_not_found'

    if type(word) is not str:
        raise Exception('translate(): expected str, but got ' + str(type(word)))

    word = word.lower().strip('\t\n\\-_-/=+')
    if word == "": return None

    page = get_func(url_base+word).text

    if err_not_found in page:
        result = f'error: cant translate the word `{word}`\n'
    else:
        result = parse_translation(page).strip() + '\n'

    similar_words = parse_similar_words(page)
    variants = parse_possible_variants(page)
    if similar_words:
        result += '\n'
        result += 'similar: '
        result += f'`{"`, `".join(similar_words)}`?'
    if variants:
        result += '\n'
        result += 'possible variants: '
        result += f'`{"`, `".join(variants)}`?'

    return result


def interactive():
    print('---- Interactive mode ----')
    with requests.Session() as session:
        try:
            inp = input('> ')
            while inp not in ['exit', 'quit', 'e', 'q']:
                if (inp in ['clear', 'c', 'cls']):
                    clear_console()
                else:
                    print('#', translate(inp, session.get), '\n')
                inp = input('> ')
        except (KeyboardInterrupt, EOFError):
            print()
            return KeyboardInterrupt

if __name__ == '__main__':
    args = sys.argv
    program_name = args.pop(0)

    if len(args) == 0:
        interactive()

    elif len(args) == 1:
        print(translate(args[0]))

    elif len(args) > 1:
        with requests.Session() as session:
            for word in args:
                transl_word = translate(word, session.get)
                print(word, '=', transl_word)
