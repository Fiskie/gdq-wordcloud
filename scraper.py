import HTMLParser
import re
import urllib2

pageExists = 1
page = 0

# Seemed to be 403ing without a user agent, let's fix that :^)

user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
headers = {'User-agent': user_agent}

eventId = raw_input('Enter event ID (12 for AGDQ 2015): ')
pageLimit = int(raw_input('Enter number of pages to parse (0 for all): '))

commentRegex = re.compile('<td class="(?:Invalid Variable: )?commentstate">\n(.*)(?:<hr>)\n<\/td>')
donorListRegex = re.compile('<a href="\/tracker\/donor\/.+">(.*)</a>\n<\/td>\n<td>\n<span class="datetime">(?:.*)</span>\n<\/td>\n<td>\n<a href="(.*)">(.*)<\/a>')
lastPageRegex = re.compile('<a href="\?page=(\d+)" class="last">')

stringMap = {}
htmlParser = HTMLParser.HTMLParser()


# Parse a donor preg object


def parse_donor(donor):
    """
    # 0: Username
    # 1: personal donation page.
    # 2: donation amount in the format $xx.xx.
    
    :param donor: list
    """

    url = 'https://gamesdonequick.com' + donor[1]
    req = urllib2.Request(url, None, headers)
    response = urllib2.urlopen(req)

    html = response.read()

    matches = commentRegex.findall(html)

    if len(matches) == 0:
        # Comment was rejected
        return

    # We have a comment, let's split the words and map them.

    comment = htmlParser.unescape(matches[0])

    print('%20s: %s' % (donor[0], comment))

    add_to_cloud(comment)


def add_to_cloud(comment):
    """
    Add a comment to the map.
    :param comment: str
    """
    
    for word in comment.split(' '):
        word = word.lower()

        if word in stringMap:
            stringMap[word] += 1
        else:
            stringMap[word] = 1

# Main loop

maxPage = 1

while maxPage > page:
    page += 1

    if pageLimit != 0 and page > pageLimit:
        print('Page limit of %d reached, stopping.' % pageLimit)
        break

    print('Downloading page %d of %d...' % (page, maxPage))

    url = 'https://gamesdonequick.com/tracker/donations/%s?page=%d' % (eventId, page)

    req = urllib2.Request(url, None, headers)
    
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError:
        print('Internal server error. Stopping.')
        break

    html = response.read()

    maxPage = int(lastPageRegex.findall(html)[0])

    for donor in donorListRegex.findall(html):
        parse_donor(donor)

# Save stringMap data to file

print('Saving lists...')

wordCount = open('word_count.txt', 'w')
wordCloud = open('word_cloud.txt', 'w')

for string in stringMap:
    count = stringMap[string]

    wordCount.write(string + ' ' + str(count) + '\n')

    for i in range (0, count - 1):
        wordCloud.write(string + ' ')

wordCount.close()
wordCloud.close()

print('Done')
