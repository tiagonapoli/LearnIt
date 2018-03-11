def markdown_options(options, markdown_options):
	cnt = 0
	ret = []
	for option in options:
		ret.append(markdown_options + option + markdown_options)
	return ret


def treat_msg_markdown(txt, args):
	stack = ['']
	ret = []
	ret_args = ()
	j = 0

	special_char = ['*', '_', '`']
	for i in range(0, len(txt) - 1):
		if txt[i] == '%' and txt[i+1] == 's' and j < len(args):
			ret_args += (treat_txt_argument(args[j], stack[-1]), )
			j += 1
		if i-1 < 0 or txt[i-1] != '\\' or (i-2 >= 0 and txt[i-2] == '\\'):
			for char in special_char:
				if txt[i] == char:
					if stack[-1] == char:
						stack.pop()
					else:
						stack.append(char)
		ret.append(txt[i])
	ret.append(txt[-1])

	return ''.join(ret) % ret_args


def treat_txt_argument(txt, inside=""):
	txt = str(txt)
	if inside == "" or inside == '_':
		txt = txt.replace('_', inside + '\_' + inside)
	if inside == "" or inside == '*':
		txt = txt.replace('*', inside + '\*' + inside)
	if inside == "" or inside == '`':
		txt = txt.replace('`', inside + '\`' + inside)		
	return txt


def treat_special_chars(text):
	ant = text 
	text = text.strip()
	#text = text.replace('/', '')
	text = text.replace('[', '')
	text = text.replace(']', '')
	#text = text.replace('\\', '')
	text = text.strip()
	text = text.replace('\n', '')
	#print("{} -> treated -> {}".format(ant,text))
	return text


def treat_username_str(username):
	if username[0] == '@':
		return username[1:]
	return username



if __name__ == '__main__':

	def test(txt, args):
		print(treat_msg_markdown(txt, args))
		print(treat_msg_markdown('wololoooooo', ()))


	txt = '_%s_ *%s asd*'
	args = ('tiago_napoli', 'gabriel*camargo')

	test(txt, args)

