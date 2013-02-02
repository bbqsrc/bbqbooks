<% 
import locale
locale.setlocale(locale.LC_ALL, invoice.get('their_locale', invoice['locale']))
%>
<!DOCTYPE html>
<html>
<head>
  <title>Tax Invoice &mdash; ${invoice['date']}</title>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
  <style type="text/css">
  html, body {
        font-family: "Myriad Pro", "Arial", sans-serif;
        background-color: gray;
  }

  p {
        padding: 0;
        margin: 0;
  }

  #invoicee {
    margin-top: 1em;
    font-size: 10pt;
  }

  #container {
        width: 768px;
        margin: 0 auto;
        background-color: white;
  }

  #header {
        padding: 10px;
  }

  #message {
        margin-top: 1em;
        padding-bottom: 0.6em;
        clear: both;
        font-size: 10pt;
        text-align: center;
  }

  #contact {
		margin-top: 0.5em;
  }

  .left {
        display: inline-block;
        padding: 0;
        margin: 0;
  }

  .right {
        float: right;
        text-align: right;
  }
  #invoicer {
        margin-top: 1em;
		font-size: 10pt;
  }

  #regarding {
        text-align: center;
        clear: both;
        font-weight: bold;
        margin-bottom: 1em;
		padding-top: 3em;
  }

  ul#details {
        list-style: none;
        margin: 0;
        padding: 0;
        padding-left: 12px;
        padding-bottom: 12px;
  }

  table#items {
        margin: 0 auto;
        width: 80%;
  }

  table#items, table#items td, table#items th {
        border-collapse: collapse;
        border: 1px solid black;
        border-width: 1px;
        padding: 0.1em 0.3em;
        line-height: 18pt;
        font-size: 12pt;
  }

  table#items th.desc {
        width: 50%;
  }


  table#totals td {
        text-align: right;
        padding-left: 10px;
        padding-right: 10px;
  }

  table#totals td.currency {
        padding-right: 6px;
  }

  table#totals td.total {
        padding-right: 0.2em;
        border: 1px solid black;
  }

  #payment {
        width: 92%;
        margin: 0 auto;
        margin-top: 3em;
        border-top: 1px dotted black;
        border-bottom: 1px dotted black;
        overflow: auto;
  }

  #business-number {
        font-size: 10pt;
  }

  #business-number:before {
        content: "ABN: ";
  }

  .payment-method {
        font-size: 10pt;
  }

  .payment-method-heading {
        margin-top: 0.7em;
        margin-bottom: 0.3em;
        font-weight: bold;
  }

  .heading {
        font-weight: bold;
		margin-top: 0.3em;
  }

  .number {
        text-align: right;
  }

  #business-number {
		margin-bottom: 1em;
  }

  #invoice-id, #invoice-date {
		font-size: 10pt;
  }

  </style>
  <style type="text/css" media="print">
    html, body {
        background-color: white;
    }
  </style>
</head>

<body>
<div id="container">

  <div id="content">
    <div id="header">
      <div class="left">
        <div id="invoice-date">
          Invoice Date: ${invoice['date']}
        </div>

        <div id="invoice-id">
          Invoice No: ${invoice['id']}
        </div>

        <div id="invoicee">
          ${invoice['name']}<br>
		  ${ljoin(invoice['address'])}
        </div>
      </div>

      <div class="right">
        <strong>Tax Invoice</strong>

        <div id="business-number">
          ${personal['business_number']}
        </div>

        <div id="invoicer">
          <div id="name">
            ${personal['name']}
          </div>

          <div id="address">
            ${ljoin(personal['address'])}
          </div>

          <div id="contact">
            % for k, v in personal['contact'].items():
				${add_contact(k,v)}
			% endfor
          </div>
        </div>
      </div>
    </div>

    <div id="regarding">
      ${invoice['regarding']}
    </div>

    <ul id="details">
      % for detail in invoice['details']:
	    ${add_detail(detail)}
	  % endfor
	</ul>

    <table id="items">
      <tr>
        <th class="desc">Description</th>

        <th>Hours/Qty</th>

        <th>Rate/Price</th>

        <th>Total Ex. Tax</th>
      </tr>
      % for row in invoice['items']:
        ${add_item(row)}
	  % endfor
    </table>
  
  </div>
  <div id="footer">
	
	<div id="payment">
      <div class="left">
        <div class="heading">
          Payment Options
        </div>

      	% for method in personal['payment_methods']:
			${add_payment_option(method)}
		% endfor
	  </div>

      <div class="right">
        <table id="totals">
		  <%
		  	total_excl_tax = 0.0
			tax = 0.0
			
			for item in invoice['items']:
				rate = float(item.get('their_rate_price', item['rate_price']))
				total_excl_tax += float(item['hours_qty']) * rate 
				tax += float(item['tax'])
			
			total_incl_tax = total_excl_tax + tax
			already_paid = float(invoice['already_paid'])
			total_due = total_incl_tax - already_paid
		  %>
          <tr>
            <td>Total Excl. Tax:</td>

            <td class="number">${cur(total_excl_tax)}</td>
          </tr>

          <tr>
            <td>Tax:</td>

            <td class="number">${cur(tax)}</td>
          </tr>

          <tr>
            <td>Total Incl. Tax:</td>

            <td class="number">${cur(total_incl_tax)}</td>
          </tr>

          <tr>
            <td>Already Paid:</td>

            <td class="number">${cur(already_paid)}</td>
          </tr>

          <tr>
            <td colspan="2"></td>
          </tr>

          <tr>
            <td>Total Due:</td>

            <td class="total">${cur(total_due)}</td>
          </tr>

          <tr>
            <td>Payment Due By:</td>

            <td class="total">${invoice['payment_due']}</td>
          </tr>

          <tr>
            <td>Reference Number:</td>

            <td class="total">${invoice['reference']}</td>
          </tr>
        </table>
      </div>
    </div>

    <div id="message">
      ${invoice['message']}
	</div>

  </div>
</div>
</body>
</html>

<%def name="add_detail(detail)">
    <li>${detail}</li>
</%def>

<%def name="add_item(item)">
    <% rate = item.get('their_rate_price', item['rate_price']) %>
      <tr>
        <td>${item['description']}</td>
        <td class="number">${num(item['hours_qty'])}</td>
        <td class="number">${cur(rate)}</td>
        <td class="number">${cur(float(rate) * float(item['hours_qty']))}</td>
      </tr>
</%def>

<%def name="ljoin(x)">
	<%
		if not isinstance(x, str):	
			x = "<br>".join(x)
	%>
	${x}
</%def>

<%def name="num(x)">
	<%
		fmt = "%.0f"
		x = locale.format(fmt, float(x), True, False)
	%>
	${x}
</%def>

<%def name="cur(x)">
	<% 
		
		side = "right" if inv_locale['currency'].get('side') == "right" else "left"
		fmt = inv_locale['currency'].get('format') or "%.2f"
		x = locale.format(fmt, float(x), True, True)
		if side == "right":
			x = "%s%s" % (x, inv_locale['currency']['symbol'])
		elif side == "left":
			x = "%s%s" % (inv_locale['currency']['symbol'], x)
		
	%>
	${x}
</%def>

<%def name="add_contact(k, v)">
	<div class="contact">${k}: ${v}</div>
</%def>

<%def name="add_payment_option(payment)">
		% for k, v in payment.items():
        <div class="payment-method">
          <div class="payment-method-heading">
            ${k}
          </div>
          ${ljoin(v)}
		% endfor
		</div>
</%def>
