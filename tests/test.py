import sys
from sheetscrape.scraper import GoogleSheetScraper

if __name__=='__main__':
    keyfile = sys.argv[1]
    print(f'Using keyfile: {keyfile}')
    print(GoogleSheetScraper(keyfile, mode='r').client.list_spreadsheet_files())
