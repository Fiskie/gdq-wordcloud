import urllib2
import re

pageExists = 1
page = 0

# Seemed to be 403ing without a user agent, let's fix that :^)

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = { 'User-agent' : user_agent }

eventId = int(raw_input('Enter event ID (12 for AGDQ 2015): '));
maxPages = int(raw_input('Enter number of pages to parse (0 for all): '));

commentRegex = re.compile('<td class="(?:Invalid Variable: )?commentstate">\n(.*)(?:<hr>)\n<\/td>')
donorListRegex = re.compile('<tr>\n<td>\n<a href="(.*)">(.*)</a>\n<\/td>\n<td>\n<span class="datetime">(?:.*)</span>\n<\/td>\n<td>\n<a href="(.*)">(.*)<\/a>\n<\/td>\n<td>\nYes\n<\/td>\n<\/tr>')

stringMap = {}

# Parse a donor preg object

def parseDonor(donor):

	# 0: donor profile page. We don't want this, it'll result in duplicates.
	# 1: Username
	# 2: personal donation page.
	# 3: donation amount in the format $xx.xx.

	print 'Getting ' + donor[1] + '\'s donation message...'
	
	url = 'https://gamesdonequick.com' + donor[2]
	req = urllib2.Request(url, None, headers)
	response = urllib2.urlopen(req)

	html = response.read()

	matches = commentRegex.findall(html)

	if len(matches) == 0:
		print 'Comment pending or rejected.'
		return

	# We have a comment, let's split the words and map them.

	comment = matches[0]

	print 'Comment: ' + comment

	addToMap(comment)

# Add a comment to the map

def addToMap(comment):
	stringList = comment.split(' ')
	
	for string in stringList:
		string = string.lower()

		if string in stringMap:
			stringMap[string] += 1
		else:
			stringMap[string] = 1

# Main loop

while pageExists:
	page += 1

	if maxPages != 0 and page > maxPages:
		print 'Page limit of ' + str(maxPages) + ' reached, quitting.'
		break;

	print 'Downloading page ' + str(page) + '...'

	url = 'https://gamesdonequick.com/tracker/donations/' + str(eventId) + '?page=' + str(page)

	req = urllib2.Request(url, None, headers)
	
	try:
		response = urllib2.urlopen(req)
	except urllib2.HTTPError:
		print 'Internal server error, assumed finished.'
		break

	html = response.read()

	donorsWithComments = donorListRegex.findall(html)

	for donor in donorsWithComments:
		parseDonor(donor)

# Save stringMap data to file

print 'Saving lists...'

wordCount = open('word_count.txt', 'w')
wordCloud = open('word_cloud.txt', 'w')

for string in stringMap:
	count = stringMap[string]

	wordCount.write(string + ' ' + str(count) + '\n')

	for i in range (0, count - 1):
		wordCloud.write(string + ' ')

wordCount.close()
wordCloud.close()

print 'Done'
