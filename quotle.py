from bs4 import BeautifulSoup
import re
from urllib import request
import requests
import json
import bs4
from tqdm import tqdm
import argparse
import sys

parser = argparse.ArgumentParser(description='Retrieve movie-specific quotes recorded in IMDb')
parser.add_argument('-t', '--title', action='store', dest='title', help='Specify movie/show title, ex: python quotle.py -t "pulp fiction"')
parser.add_argument('-o', '--out', action='store_true', help='Write quotes to .txt file with filename as titlename')

if len(sys.argv[1:]) == 0:
    parser.print_help()
    parser.exit()

args = parser.parse_args()

def parse_titles(string):

    index = 1
    string = string.replace(' ','+')

    #Using OMDb API
    response = request.urlopen('http://www.omdbapi.com/?apikey=d0b356ff&s='+string)
    data = json.loads(response.read())
    Search = data['Search']

    for item in Search:
        print(str(index) + '. ' + item['Title'] + ' (' + item['Year'] + ')')
        index += 1

    choice = int(input("\nChoose your title 1, 2, 3...: "))
    imdbID, mname = (Search[choice - 1]['imdbID']), Search[choice - 1]['Title'] + ' ' + '(' + Search[0]['Year'] + ')'

    return mname, imdbID

def scrape_quotes(imdbID, title, filename=None):

    page = requests.get('https://www.imdb.com/title/' + imdbID + '/quotes')

    #Extract quotes
    quotes = []
    soup = BeautifulSoup(page.content, 'html.parser')
    containers = soup.findAll('div', class_='sodatext')
    # cnt_len = len(containers) - 1

    for container in containers:
        quotes.append('\n')
        quotelists = container.findAll('p')

        for quotelist in quotelists:
            quotes.append(quotelist.text)

    #Remove unnecessary new lines
    i = 0
    for quote in quotes:
        x = re.sub('\\n', ' ', quote)
        quotes[i] = x
        i = i + 1

    for quote in quotes:
        print(quote)

    if len(quotes) != 0:
        print('\n' + 'Found quotes and ' + str(len(containers)) + ' conversations for ' + title)
        if filename is None:
            print('Use -o ' + title + 'to get all available quotes into a text file if only the last few quotes are displayed on the console.\n')
    else:
        print('There seems to be no quotes recorded for ' + title)

    def write_to_text(filename):
        doc = open(filename, 'w')
        for quote in tqdm(quotes):
            doc.write(quote + '\n')
        doc.close()

    if filename is not None:
        write_to_text(filename)
        print('Recorded quotes in plaintext')

if args.title:
    title = args.title.replace(' ', '+')
    try:
        mname, imdbID = parse_titles(title)
    except:
        print('Oops, that title does not exist in IMDb')
    if args.out:
        scrape_quotes(imdbID, mname, str(mname + '.txt'))
    else:
        scrape_quotes(imdbID, mname)
        