import csv

stocks = []
with open('ihsg.csv') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    for row in reader:
       stocks.append(row[1])

from jinja2 import Template

template = '''
{%- for stock in stocks -%}
- code: {{ stock }}
  country: JK
{% endfor %}
'''

tm = Template(template)
msg = tm.render(stocks=stocks)

print(msg)
