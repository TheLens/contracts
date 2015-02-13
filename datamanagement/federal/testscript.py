import json
from pprint import pprint
json_data=open('/home/abe/Downloads/contributions_richmond.json')

data = json.load(json_data)

json_data.close()


#Get header
contribution = data[0]

for k in contribution.keys():
	line = []
	for k in contribution.keys():
		line.append(k)

print ",".join(line)

#print len(contributions)

for contribution in data:
	line = []
	for k in contribution.keys():
		print line.append(str(contribution[k]))

	print ",".join(line)