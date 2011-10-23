from mako.template import Template
from mako.lookup import TemplateLookup
from collections import OrderedDict
from os.path import join as pjoin

import mako
import json, re, sys, os
import readline
import types


__version__ = "0.2dev"
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
		self.changes = False

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
		def set_menu(m):
			self.current_menu = m

		def toggle_advanced():
			self.advanced_mode = not self.advanced_mode
			print("Advanced mode:", self.advanced_mode)
		
		self.menu = (
			('new', 'open a new book', self.new_book),
			('load', 'load a book', self.load_book),
			('quit', 'exit the application', self.quit, 'q')
		)

		self.book_menu = (
			('add invoice', 'adds a new invoice', self.add_invoice),
			('output invoice', 'outputs an invoice to file', self.output_invoice),
			('output invoices', 'outputs all invoices to directory', self.output_all_invoices),
			('personal settings', 'set your details and preferences', lambda: set_menu(self.personal_menu)),
			('save', 'save the current book', self.save_book, 's'),
			('quit', 'exit the application', self.quit, 'q')
		)

		self.personal_menu = (
			('set details', 'change name, address, etc', self.set_personal_details),
			('advanced mode', 'enable/disable advanced functionality', toggle_advanced),
			('return to invoice menu', 'go back to invoice menu', lambda: set_menu(self.book_menu), 'r')

		)

		self.current_menu = self.menu

	def create_dict_from_questions(self, questions, default_dict):
		data = OrderedDict()
		res = ""
		for q in questions:
			print(q[0])
			
			if isinstance(q[2], types.FunctionType):
				res = q[2]()

			elif q[2] is True:
				res = ""
				while 1:
					last = input("> ")
					res += last
					if last.strip() != "":
						res += "\n"
					else:
						break
				res = res.strip().split("\n")

			elif q[2] is False:
				res = input("[%s]> " % default_dict.get(q[1], "")).strip()
				if res == "":
					res = default_dict.get(q[1], "")

			data[q[1]] = res
		return data



				
	def set_personal_details(self):
		self.changes = True
		def set_contact():
			contacts = {}
			while 1:
				typ = input("Type > ").strip()
				if typ == "":
					break
				acct = input("Value > ").strip()
				contacts[typ] = acct
			return contacts

		def set_payment():
			payment = []
			while 1:
				method = input("Method > ").strip()
				if method == "":
					break
				
				print("Text")
				res = ""
				while 1:
					last = input("> ")
					res += last
					if last != "":
						res += "\n"
					else:
						break
				text = res.strip().split('\n')
				payment.append({method: text})


		questions = (
			("Name", "name", False, ""),
			("Address", "address", True, ""),
			("Contact", "contact", set_contact, {}),
			("Business number", "business_number", False, ""),
			("Payment methods", "payment_methods", set_payment, []),
			("Default template", "default_template", False, "default.tpl"),
			("Default locale", "default_locale", False, "en_AU")#,
			#("Logo (base64)", "logo", False, None)
		)
		data = self.create_dict_from_questions(questions, self.book.data['personal'])
		self.book.data['personal'] = data
		print("Personal data modified.")
	

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
			("Message", "message", False, "")#,
			#("Template", "template", True)
			#("Locale", "locale", False)
		)
		data['template'] = 'default.tpl'
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
		print("Enter invoice code you wish to output.")
		res = input("> ")
		if self.book.inv_code_exists(res.strip()):
			inv_code = res.strip()

		print("Please enter the file you wish to save the output to.")
		res = input("> ")
		if not res.endswith('.html'):
			res += ".html"
		f = None
		try:
			f = open(res, 'w')
			self.book.output_invoice(inv_code, f)
			f.close()
		except IOError:
			print("File not writable.")
	
	def output_all_invoices(self):
		print("Please enter directory you wish to save all invoices to.")
		res = input("> ")
		try:
			os.makedirs(res)
		except OSError as e:
			if e.errno != 17:
				print(e)
				return

		for inv_code in self.book.data['invoices'].keys():
			f = open(pjoin(res, inv_code + ".html"), 'w')
			self.book.output_invoice(inv_code, f)
			f.close()

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
			print("Enter the path you wish to save the file to.")
			sel = input("> ")
			if not sel.endswith(__fileext__):
				sel += __fileext__

		f = open(sel, 'w')
		self.book.save(f)
		f.close()
		self.changes = False
		self.fn = sel
		print("File %s saved." % self.fn)

	def run_menu(self):
		self.define_menus()
		while 1:
			c = 1
			cmds = {}
			print('\n---')
			for item in self.current_menu:
				if len(item) < 4:
					print("%2s) %16s - %s" % (c, item[0], item[1]))
					cmds[str(c)] = item[2]
					c += 1
				else:
					print("%2s) %16s - %s" % (item[3], item[0], item[1]))
					cmds[item[3]] = item[2]
			print()	
			try:
				sel = input("> ").strip()
				if sel in cmds:
					cmds[sel]()
				else:
					print("Invalid selection")
			except (EOFError, KeyboardInterrupt):
				self.quit()
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
		
	def inv_code_exists(self, inv_code):
		return self.data['invoices'].has_key(inv_code)
	
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

	def output_invoice(self, inv_code, f):
		invoice = self.generate_invoice(inv_code)
		if invoice is not None:
			f.write(invoice)


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
		"address": [],
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
			"address": ["Long Address", "Some Place"],
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

if __name__ == "__main__":
	ui = BookTUI()
	ui.start()

