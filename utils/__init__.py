import os

def valida_cnpj(cnpj):
	ci = [int(i) for i in cnpj if i.isdigit()]

	if len(ci) != 14 or str(ci) == "1"*14:
		return

	cnpj = ''.join([str(x) for x in ci])

	soma = ci[0] * 5
	soma = soma + (ci[1] * 4)
	soma = soma + (ci[2] * 3)
	soma = soma + (ci[3] * 2)
	soma = soma + (ci[4] * 9)
	soma = soma + (ci[5] * 8)
	soma = soma + (ci[6] * 7)
	soma = soma + (ci[7] * 6)
	soma = soma + (ci[8] * 5)
	soma = soma + (ci[9] * 4)
	soma = soma + (ci[10] * 3)
	soma = soma + (ci[11] * 2)

	soma = soma - (11 * int(soma / 11))

	if soma in [0, 1]:
		result1 = 0
	else:
		result1 = 11 - soma

	if result1 == ci[12]:
		soma = ci[0] * 6
		soma = soma + (ci[1] * 5)
		soma = soma + (ci[2] * 4)
		soma = soma + (ci[3] * 3)
		soma = soma + (ci[4] * 2)
		soma = soma + (ci[5] * 9)
		soma = soma + (ci[6] * 8)
		soma = soma + (ci[7] * 7)
		soma = soma + (ci[8] * 6)
		soma = soma + (ci[9] * 5)
		soma = soma + (ci[10] * 4)
		soma = soma + (ci[11] * 3)
		soma = soma + (ci[12] * 2)

		soma = soma - (11 * int(soma / 11))

		if soma in [0, 1]:
			result2 = 0
		else:
			result2 = 11 - soma

		if result2 == ci[13]:
			return "%s.%s.%s/%s-%s" % (cnpj[:2],cnpj[2:5],cnpj[5:8],cnpj[8:12],cnpj[12:])

def get_file_list(diretorio_origem, diretorio_destino, lista_diretorios_descartados):

	return_list = []
	lista_diretorios_descartados = lista_diretorios_descartados or []

	file_list = [x for x in os.listdir(diretorio_origem) if x not in lista_diretorios_descartados]

	for value in file_list:
		real_file = os.path.join(diretorio_origem, value)

		if os.path.isdir(real_file):
			return_list.extend(get_file_list(real_file, os.path.join(diretorio_destino, value), lista_diretorios_descartados))
		else:
			return_list.append(real_file)

	return return_list

if __name__ == '__main__':
	import pdb; pdb.set_trace()
	from pprint import pprint
	pprint(get_file_list(os.sep.join([os.getcwd(), 'update']), os.getcwd(), []))