from .. import GoogleSheetScraper
import sys

if __name__ == "__main__":
    keyfile = sys.argv[1]
    print(f"Using keyfile: {keyfile}")
    print(GoogleSheetScraper(keyfile, access_mode="r").client.list_all_spreadsheets())
