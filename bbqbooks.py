from mako.template import Template
from mako.lookup import TemplateLookup
from collections import OrderedDict

import mako
import json, re, sys
import readline

__version__ = "0.1"
__author__ = "Brendan Molloy"
__fileext__ = ".bbqbook"
def yes_no_prompt(default=None):
	prompt = ""
	
	if default:	
		if default.lower() == "y":
			prompt += "Y"
		else:
			prompt += "y"
		
		prompt += "/"
	
		if default.lower() == "n":
			prompt += "N"
		else:
			prompt += "n"
	else:
		prompt = "y/n"

	while 1:
		res = input("[%s]> " % prompt)
		if res == "":
			res = default.lower()
		
		if res.strip().lower() == "n":
			return False

		elif res.strip().lower() == "y":
			return True

class BookTUI:
	def __init__(self):
		self.book = None
		self.fn = None
		self.advanced_mode = False
		self.changes = True

	def start(self):
		print("bbqbooks %s" % __version__)
		print("Copyright (c) 2011 %s" % __author__)
		print("Make you yourself a selection innit.")
		self.run_menu()

	def quit(self):
		if self.book and self.changes:
			print("You have an open book. Do you want to save?")
			res = yes_no_prompt("y")

			if res and self.fn:
				print("Saved to %s" % res)
			elif res:
				self.save_as_book()

		sys.exit()
	
	def define_menus(self):
		def toggle_advanced():
			self.advanced_mode = not self.advanced_mode
			print("Advanced mode:", self.advanced_mode)
		
		self.menu = (
			('new', 'open a new book', self.new_book),
			('load', 'load a book', self.load_book),
			('quit', 'exit the application', self.quit)
		)

		self.book_menu = (
			('add invoice', 'adds a new invoice', self.add_invoice),
			('output invoice', 'outputs an invoice to file', self.output_invoice),
			('output invoices', 'outputs all invoices to directory', self.output_all_invoices),
			#('advanced mode', 'enable/disable advanced functionality', toggle_advanced),
			('save', 'save the current book', self.save_book),
			('quit', 'exit the application', self.quit)
		)

		self.current_menu = self.menu

	def add_invoice(self):
		self.changes = True

		data = OrderedDict()
		data['id'] = str(len(self.book.data['invoices'])+1)
		data['items'] = []
		
		def add_item():
			questions = (
				("Description", "description", False, ""),
				("Hours/Qty", "hours_qty", False, 0),
				("Rate/Price", "rate_price", False, 0),
				("Tax", "tax", False, 0)
			)
			
			item = OrderedDict()
			res = ""
			for q in questions:
				print(q[0])
				
				res = ""
				while 1:
					last = input("> ")
					res += last
					if q[2] and last != "":
						res += "\n"
					else:
						break
				
				res = res.strip()

				if res == "":
					if q[1] == "description":
						break
					res = q[3]

				item[q[1]] = res

			if res == "":
				return False
			
			data['items'].append(item)
			return True


		questions = (
			("Invoicee's name", "name", False, ""),
			("Invoicee's address", "address", True, ""),
			("Date (leave blank for today)", "date", False, ""),
			("Regarding", "regarding", False, ""),
			("Details (each item on new line)", "details", True, ""),
			("Items", "items", True, ""),
			("Payment due", "payment_due", False, ""),
			("Already paid", "already_paid", False, 0),
			("Reference code", "reference", False, ""),
			("Message", "message", True, "")#,
			#("Template", "template", True)
			#("Locale", "locale", False)
		)
		data['template'] = 'template.tpl'
		data['locale'] = "en_AU"
		
		
		for q in questions:
			print(q[0])
			if q[1] == "items":
				while 1:
					if not add_item():
						break
				continue

			res = ""
			while 1:
				last = input("> ")
				res += last
				if q[2] and last != "":
					res += "\n"
				else:
					break
			res = res.strip()
			if res == "":
				res = q[3]
		
			if '\n' in res:
				res = res.split('\n')

			data[q[1]] = res

		for k, v in data.items():
			if isinstance(v, list):
				print("%s:" % k)
				if isinstance(v[0], dict):
					for n, dct in enumerate(v):
						print(" %s." % n)
						for kk, vv in dct.items():
							print("  %s: %s" % (kk, vv))
				else:
					print("  " + "\n  ".join(v))
			else:
				print("%s: %s" % (k, v))
		
		print("Is this correct?")
		if yes_no_prompt('y'):
			self.book.data['invoices'][data['id']] = data
			print("Created new invoice number %s." % data['id'])
	
	def output_invoice(self):
		pass
	
	def output_all_invoices(self):
		pass
	
	def new_book(self):
		self.book = Book()
		self.current_menu = self.book_menu
		print("New book created.")

	def load_book(self):
		self.book = Book()
		print("Please enter path to book file (%s)" % __fileext__)
		sel = input("> ")
		f = None
		try:
			f = open(sel, 'r')
		except IOError as e:
			try:
				if not sel.endswith(__fileext__):
					sel += __fileext__
					f = open(sel, 'r')
			except:
				print("File not found or not readable.")
				return
		
		self.book.load(f)
		self.fn = sel
		f.close()
		
		self.current_menu = self.book_menu
		print("File loaded successfully.")

	def save_book(self):
		self.save_as_book(self.fn)		

	def save_as_book(self, sel=None):
		if not sel:
			print("Enter the path you wish to save the file to")
			sel = input("> ")
			if not sel.endswith(__fileext__):
				sel += __fileext__

		f = open(sel, 'w')
		self.book.save(f)
		f.close()
		self.changes = False
		print("File %s saved." % self.fn)

	def run_menu(self):
		self.define_menus()
		while 1:
			print('\n---')
			for n, item in enumerate(self.current_menu):
				print("%2s) %16s - %s" % (n+1, item[0], item[1]))
			print()	
			try:
				sel = input("> ")
				sel = int(sel)-1
				if sel < len(self.current_menu) and sel >= 0:
					self.current_menu[sel][2]()
				else:
					print("Invalid selection")
			except (EOFError, KeyboardInterrupt):
				sys.exit()
			except ValueError:
				print("Invalid selection")
				



class Book:
	def __init__(self):
		self.data = json.loads(default_config)

	def load(self, f):
		self.data = json.load(f)
		self.data['template_path'] = [
			'.',
			'templates'
		]

	def save(self, f):
		json.dump(self.data, f)

	def merge_data_for_invoice(self, invoice):
		return {
			'invoice': invoice,
			'personal': self.data['personal'],
			'inv_locale': self.data['locales'][invoice['locale']]
		}
		

	def generate_invoice(self, inv_code):
		invoices = self.data.get("invoices")
		if invoices is None:
			self.data['invoices'] = {}

		invoice = self.data['invoices'].get(inv_code)
		if invoice is None:
			print("Invoice not found!")

		tl = TemplateLookup(directories=self.data['template_path'])
		try:
			template = tl.get_template(invoice['template'])
			return template.render(**self.merge_data_for_invoice(invoice))
		except:
			print(mako.exceptions.text_error_template().render())

	def output_invoice(self, inv_code, fn):
		invoice = self.generate_invoice(inv_code)
		if invoice is not None:
			f = open(fn, 'w')
			f.write(invoice)
			f.close()
			print("%s saved." % fn)
		else:
			print("File not saved.")

def test():
	import io
	book = Book()
	book.load(io.StringIO(example_config))
	book.output_invoice('1', "invoice-test.html")
	book.save("./meow.json")

default_config = r"""
{
	"personal": {
		"name": "",
		"address": "",
		"contact": {},
		"business_number": "",
		"payment_methods": [],
		"default_template": "default.tpl",
		"default_locale": "en_AU",
		"logo": null
	},

	"invoices": {},
	
	"locales": {
		"en_AU": {
			"currency": {
				"symbol": "$",
				"format": "%.2f",
				"code": "AUD",
				"side": "left"
			}
		},
		"no_NO": {
			"currency": {
				"symbol": "kr",
				"format": "%.2f",
				"code": "NOK",
				"side": "right"
			}
		},
		"de_DE": {
			"currency": {
				"symbol": "€",
				"format": "%.2f",
				"code": "EUR",
				"side": "right"
			}
		}
	}

}
"""

example_config = r"""
{
	"personal": {
		"name": "John Smith",
		"address": "123 Fake Street<br>Some Place",
		"contact": {
			"Mobile": "0499 999 999",
			"Email": "john@smith.name"
		},
		"business_number": "123 123 123 12",
		"payment_methods": [
			{
				"method": "Direct Deposit &mdash; Australia",
				"text": "John Smith<br>BSB: 123 123<br>Account Number: 123 123 123"
			},
			{
				"method": "Direct Deposit &mdash; Worldwide",
				"text": "No idea. Try again later."
			}
		],
		"default_template": "default.tpl",
		"default_locale": "en_AU",
		"logo": null
	},

	"locales": {
		"en_AU": {
			"currency": {
				"symbol": "$",
				"format": "%.2f",
				"code": "AUD",
				"side": "left"
			}
		},
		"no_NO": {
			"currency": {
				"symbol": "kr",
				"format": "%.2f",
				"code": "NOK",
				"side": "right"
			}
		},
		"de_DE": {
			"currency": {
				"symbol": "€",
				"format": "%.2f",
				"code": "EUR",
				"side": "right"
			}
		}
	},

	"invoices": {
		"1": {
			"id": "1",
			"name": "Some Person",
			"address": "Long Address<br>Some Place",
			"date": "2011-02-02",
			"regarding": "RE: Something Good",
			"details": [
				"Farts",
				"Good Smells"
			],
			"items": [
				{
					"description": "Example thing 1",
					"hours_qty": 5,
					"rate_price": 20.99,
					"tax": 10
				},
				{
					"description": "Example thing 2",
					"hours_qty": 5,
					"rate_price": 20,
					"tax": 10
				}
			],
			"payment_due": "2011-10-02",
			"reference": "ANYTHING",
			"locale": "de_DE",
			"already_paid": 40.00,
			"message": "<strong>Thank you</strong> for your purchase.",
			"template": "default.tpl"
		}
	}
}
"""
