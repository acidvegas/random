#!/usr/bin/env python
# CraigsList Parser - Developed by acidvegas in Python (https://acid.vegas/random)

'''
Random script to parse all the countries, states, cities, & sections/sub-sections on CraigsList
'''

import re, time, urllib.request

def between(source, start, stop):
	data = re.compile(start + '(.*?)' + stop, re.IGNORECASE|re.MULTILINE).search(source)
	return data.group(1) if data else False

def get_source(url):
	source = urllib.request.urlopen(url, timeout=10)
	charset = source.headers.get_content_charset()
	return source.read().decode(charset) if charset else source.read().decode()

db        = {'category':dict(),'subcat':dict()}
source    = get_source('http://www.craigslist.org/about/sites?lang=en&cc=us')
countries = re.findall('<h1><a name="(.*?)"></a>(.*?)</h1>', source, re.IGNORECASE|re.MULTILINE)
source    = source.replace('\n', '').replace('\r','')
main_data = dict()
statess = 0
citiess = 0
for country in countries:
	main_data[country[0].lower()] = dict()
	data   = between(source, '<h1><a name="{0}"></a>{1}</h1>'.format(country[0], country[1]),'</a></li>                    </ul>                </div>            </div>')
	states = re.findall('<h4>(.*?)</h4>', data, re.IGNORECASE|re.MULTILINE)
	statess += len(states)
	for state in states:
		main_data[country[0].lower()][state.lower()] = dict()
		state_data = between(source, f'<h4>{state}</h4>', '</ul>')
		cities = re.findall('<li><a href="(.*?)">(.*?)</a></li>', state_data, re.IGNORECASE|re.MULTILINE)
		citiess += len(cities)
		for city in cities:
			main_data[country[0].lower()][state.lower()][city[1]] = city[0].split('/?')[0]
			new_source = get_source(city[0].split('/?')[0])
			new_source = new_source.replace('\n', '').replace('\r','')
			categories = re.findall('data-alltitle="all (.*?)" data-cat="(.*?)">', new_source, re.IGNORECASE|re.MULTILINE)
			for category in categories:
				db['category'][category[0]] = db['category'][category[0]]+1 if category[0] in db['category'] else 1
				if category[0] != 'resumes':
					cat = category[0].replace(' ','-')
					category_data  = between(new_source, f'<h4 class="ban"><a href="/d/{cat}/search', '</ul></div></div>')
					try:
						sub_categories = re.findall('span class="txt">(.*?)<sup class', category_data, re.IGNORECASE|re.MULTILINE)
						for sub_category in sub_categories:
							print(f'{country[1]} | {state} | {city[1]} | {category[0]} | {sub_category}')
							db['subcat'][sub_category] = db['subcat'][sub_category]+1 if sub_category in db['subcat'] else 1
					except:
						print('\n\n\nerror !!!')
						print(category_data)
						print(category)
						input('')
print(f'Country : {len(main_data)}')
print(f'State   : {statess}')
print(f'City    : {citiess}')
print(str(db['category']))
print('\n\n\n')
print(str(db['subcat']))
