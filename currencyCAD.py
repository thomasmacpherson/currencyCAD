import sys
if sys.version[0] != '3':
	print ('You must run currencyCAD with python3')
	sys.exit(0)

from urllib.request import urlopen
import pifacecad.tools
import pifacecad
from time import sleep
from pifacecad.tools.question import LCDQuestion

cad = pifacecad.PiFaceCAD()

currenciesUrl = "https://www.google.com/finance/converter"
currencies = urlopen(currenciesUrl)
currencies = str(currencies.read())
currencies = currencies.split('<select name=from value="">\\n')[1]
currencies = currencies.split('</select>')[0]
currencies = currencies.replace('<option  value="',',')
currencies = currencies.replace('">',',')
currencies = currencies.replace('</option>\\n',',')
currencies = currencies.split(',')
currencies.remove('')

availableCurrecies = []
for x in currencies:
	if len(x) == 3:
		availableCurrecies.append(x)

# print(availableCurrecies)

# fromCurrency = availableCurrecies[int(input("Enter from Currency:"))]
# toCurrency = "GBP"
# amount = 2
cad.lcd.cursor_off()
cad.lcd.backlight_on()
question = LCDQuestion(question="Load presets", answers=["Yes","No"])
answer = question.ask()

if not answer:
	f = open('currencyPairs','r')
	currencyPairs =[]
	for line in f:
		line = line.replace("\n","")
		pair = line.split(" ")
		currencyPairs.append(pair)
	f.close()

	# currencyPairs = [["GBP","JPY"],["USD","GBP"],["USD","JPY"]]
	availableCurrecies = []
	for pair in currencyPairs:
		availableCurrecies.append(pair[0] + ">" + pair[1])

	while cad.switches[4].value != 1:
		scanner = pifacecad.tools.LCDScanf(format="%4i.%2i %m%r", custom_values=availableCurrecies)
		request = scanner.scan()
		# print(request)
		while request[0] ==0 and request[1] ==0:
			cad.lcd.clear()
			cad.lcd.write("Must give an")
			cad.lcd.set_cursor(0,1)
			cad.lcd.write("amount!")
			sleep(2)
			cad.lcd.clear()
			scanner = pifacecad.tools.LCDScanf(format="%4i.%2i %m%r", custom_values=availableCurrecies)
			request = scanner.scan()

		amount = (request[0]) + (request[1]*.1)

		fromCurrency = currencyPairs[availableCurrecies.index(request[2])][0]
		toCurrency = currencyPairs[availableCurrecies.index(request[2])][1]


		url = "https://www.google.com/finance/converter?a={amount}&from={fromCurrency}&to={toCurrency}".format(amount=str(amount),fromCurrency=fromCurrency, toCurrency=toCurrency)

		response = urlopen(url)
		html = str(response.read())


		html = html.split("= <span class=bld>")[1]
		result = float(html.split(" " +toCurrency)[0])
		cad.lcd.set_cursor(0,0)

		cad.lcd.set_cursor(0,1)
		cad.lcd.cursor_off()
		cad.lcd.write(format(result, '.2f'))
		print(format(result,'.2f'))
		while cad.switches[0].value !=  1:
			if cad.switches[4].value:
				break
			sleep(.2)
		cad.lcd.clear()


else:
	while cad.switches[4].value != 1:
		scanner = pifacecad.tools.LCDScanf(format="%4i.%2i %m>%m%r", custom_values=availableCurrecies)
		request = scanner.scan()
		# print(request)
		while request[2] == request[3] or (request[0] ==0 and request[1] ==0):
			cad.lcd.clear()
			if request[2] == request[3]:
				cad.lcd.write("Use different")
				cad.lcd.set_cursor(0,1)
				cad.lcd.write("currencies!")
				sleep(2)
			elif request[0]==0 and request[1]==0:
				cad.lcd.write("Must give an")
				cad.lcd.set_cursor(0,1)
				cad.lcd.write("amount!")
				sleep(2)
			cad.lcd.clear()
			scanner = pifacecad.tools.LCDScanf(format="%4i.%2i %m>%m%r", custom_values=availableCurrecies)
			request = scanner.scan()

		amount = (request[0]) + (request[1]*.1)

		fromCurrency = request[2]
		toCurrency = request[3]


		url = "https://www.google.com/finance/converter?a={amount}&from={fromCurrency}&to={toCurrency}".format(amount=str(amount),fromCurrency=fromCurrency, toCurrency=toCurrency)

		response = urlopen(url)
		html = str(response.read())


		try:
			html = html.split("= <span class=bld>")[1]
		except IndexError:
			print("For some reason, Google finance converter does not convert between those currencies")
			cad.lcd.clear()
			cad.lcd.write("Google cant conv\nthose currencies")
			sleep(2)
			sys.exit()

		result = float(html.split(" " +toCurrency)[0])
		cad.lcd.set_cursor(0,0)

		cad.lcd.set_cursor(0,1)
		cad.lcd.cursor_off()
		cad.lcd.write(format(result, '.2f'))
		print(format(result,'.2f'))
		written = False
		while cad.switches[0].value !=  1:
			if cad.switches[4].value:
				break
			sleep(.2)
			if cad.switches[1].value == 1 and not written:
				written = True
				f = open('currencyPairs','r')
				pairs =[]
				for line in f:
					line = line.replace("\n","")
					pair = line.split(" ")
					pairs.append(pair)
				f.close()
				currentPair = [fromCurrency, toCurrency]	
				if currentPair not in pairs:	
					f = open('currencyPairs','a')
					f.write(fromCurrency + " " + toCurrency + "\n")
					cad.lcd.set_cursor(0,1)
					print("Pair saved")
					cad.lcd.write("Pair saved")

		cad.lcd.clear()
