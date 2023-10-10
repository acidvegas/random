#/usr/bin/env python
# LibreScrape - developed by acidvegas in python (https://git.acid.vegas/librescrape)

import urllib.request
import urllib.parse
import json
import random
import ssl

context = ssl._create_unverified_context()

def get_instances() -> list:
	'''Get instances from LibreY and Librex'''
	instances = list()
	sources = ['https://raw.githubusercontent.com/Ahwxorg/LibreY/main/instances.json',]
	for item in sources:
		data = json.loads(urllib.request.urlopen(item).read().decode())
		instances += [item['clearnet'] for item in data['instances']]
	return instances

def search(instance, query, page=1, type=0):
	'''
	Search for a query on a Libre instance

	:param instance: The instance to search on
	:param query: The query to search for
	:param page: The page number to search on (first page is 0)
	:param type: The type of search to perform (0=text, 1=image, 2=video, 3=torrent, 4=tor)

	API will return a list of results in the following format:
		[
			{
				"title": "Title of the post",
				"url": "URL of the post",
				"baseurl": "Base URL of the instance",
				"description": "Description of the post"
			},
		]
	'''
	results = urllib.request.urlopen(f'{instance}api.php?q={query}&p={page}&t={type}', context=context, timeout=5).read().decode()
	return json.loads(results)

if __name__ == '__main__':
	found = list()
	query = input('Search query: ')
	query = urllib.parse.quote(query)
	latest_instances = get_instances()
	with open('output.log', 'w') as out:
		for i in range(100):
			complete = False
			while complete is False:
				instance = random.choice(latest_instances)
				try:
					results = search(instance, query, page=i)
					for result in results:
						title = result['title']
						title = title.replace('\n','')
						while '  ' in title:
							title = title.replace('  ',' ')
						print(f'{title} - {result["url"]}')
						out.write(f'{title} - {result["url"]}\n')
				except Exception as ex:
					print('!!!' + str(ex))
					print(results)
					print('')
				else:
					completed = True
