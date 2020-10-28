import requests
import re
import sys
from base64 import b64decode, b64encode
import os
def clear_console():
	#os.system('cls')	# windows
	os.system('clear') # unix 

def translate(word, get_func=requests.get):
	if not(type(word) is str):
		return None
	word = word.lower().strip('\t\n\\-_-/=+')
	if (word == ""): return ""
		
	url_base = 'https://wooordhunt.ru/word/'
	err404 = 'Упссс'
	ru_alph = 'йцукенгшщзхъфывапролджэячсмитьбюё'
	page = get_func(url_base+word).text
	if(err404 in page):
		return 'not found'
	if(word[0] in ru_alph):
		pattern = r"<p class=\"t_inline\">(.*?)</p> <\/div"
	else:
		pattern = r'<span class=\"t_inline_en\">(.*?)<\/span> <div'
	matchObj = re.search(pattern,page, re.M|re.I)
	if matchObj: 
		res = matchObj.group(1)
		return res
	pattern = '<div class="block similar_words">(.*?)</div>'
	matchObj = re.search(pattern,page, re.M|re.I)
	if not matchObj: return "error"
	res = []
	tmp = matchObj.group(1)
	while True:
		e = tmp.find('</a>')
		if (e == -1): break
		b = tmp[:e].rfind('>')
		res.append(tmp[b+1:e])
		tmp = tmp[e+3:]
	return "maybe you mean '%s' ?" % ("', '".join(res))


def interactive():
	print('---- Interactive mode ----')
	with requests.Session() as session:
		inp = input('> ')
		while inp not in ['exit', 'quit', 'e', 'q']:
			if (inp in ['clear', 'c', 'cls']):
				clear_console()
			else:
				for word in inp.split():
					print('#', translate(word, session.get), '\n')
			inp = input('> ')
	return 0
	
if __name__ == '__main__':
	if len(sys.argv) == 1:
		interactive()
	elif len(sys.argv) == 2:
		print(translate(sys.argv[1]))
	elif len(sys.argv) > 2:
		with requests.Session() as session:
			for word in sys.argv[1:]:
				transl_word = translate(word, session.get)
				print(word, '=', transl_word)
	else:
		exit("Usage: translate.py word")
