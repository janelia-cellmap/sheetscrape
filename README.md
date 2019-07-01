## Sheetscrape: a spreadsheet scraper
Parse cloud-backed human-sourced data into a 
machine-readable data structure.

### Motivation

A large amount of useful metadata about crops has been stored via human input in spreadsheets.
In order to connect this metadata to programs that process the data, we can take the following steps:

0. Define a data structure that "represents" the crop. This will be the common currency of the following operations. 
As of this writing, I have defined a data structure, called a `FIBSEMDataset`, in this [file](https://github.com/janelia-cosem/sheetscrape/blob/master/sheetscrape/datastructures.py#L5). 

1. Parse the spreadsheet, i.e., for each row of the spreadsheet, use the data in that row to construct a `FIBSEMDataset`.

2. Insert the structured data into a database. Using a database means that the code consuming the crop metadata doesn't need to know anything about spreadsheet parsing.

Later, programs can query the database to acquired machine-readable metadata. 

## Examples
### Scraping crop metadata from the COSEM Proofreading spreadsheet

```python
from sheetscrape.scraper import GoogleSheetScraper
from sheetscrape.parsers.TrainingData import parse
import pandas as pd

# A credential file is necessary in order for this program to access a particular google sheet. 
# I created this file using the instructions here: https://gspread.readthedocs.io/en/latest/oauth2.html 
credfile = '/Users/bennettd/Downloads/cosem-db-a65771c5a9fa.json'

sheet = GoogleSheetScraper(credfile, mode='r').client.open('COSEM')
# convert the sheet to a dataframe
df = pd.DataFrame(sheet.worksheets()[0].get_all_values())
# convert the dataframe to a dict of FIBSEMDatasets, keyed by their parent filepath
datasets = parse(df)
# print out a single FIBSEMDataset
print(list(datasets.values(),)[0][0])
```
Which produces this:
```
FIBSEMDataset(biotype='HeLa', alias='Crop 33 / Mito 001', dimensions={'x': 200, 'y': 200, 'z': 200}, ...
```

## Adding scraped FIBSEMDatasets to the database
I have set up a MongoDB instance on a VM here at Janelia. Adding FIBSEMDatasets to that database is simple:
```python
from pymongo import MongoClient
import urllib.parse

# the `parse` function used earlier returns a dictionary of lists. We need a flat list, so here we flatten that dict-of-lists.
# this creates a list of FIBSEMDatasets
flat = []
for list_of_crops in datasets.values():
    [flat.append(x.todict()) for x in list_of_crops]

# Connect to the MongoDB instance
# not sure if this urllib stuff is necessary, I saw it used in an example 
un = urllib.parse.quote_plus('$USERNAME')
pw = urllib.parse.quote_plus('$PASSWORD')
db_name = '$MONGO_DB_NAME'

# insert each element in the list into the `datasets` collection on our MongoDB instance
with MongoClient(f'mongodb://{un}:{pw}@{db_name}.int.janelia.org') as client:
    db = client.db
    db.datasets.insert_many(flat)
```
## Generating FIBSEMDatasets from the Monogo database
Now suppose you are processing Crop 33 and you want to get all the metadata for that crop. Now that the database has been populated, you can just make the right query to the database:

```python
from sheetscrape.datastructures import FIBSEMDataset

with MongoClient(f'mongodb://{un}:{pw}@{db_name}.int.janelia.org') as client:
    db = client.db
    ds = db.datasets
    # set up the query-- we want all the records with the `alias` matching `Crop 33 / Mito 001` (in our case this is just 1 record).
    result = ds.find({'alias':'Crop 33 / Mito 001'})
    # result is an interable that we need to unpack
    results = [f for f in result]
    # remove the `_id` key, which a mongodb-internal thing
    [r.pop('_id') for r in results];

# construct a FIBSEMDataset with dictionary unpacking
fsb = FIBSEMDataset(**results[0])
print(fsb)
```
Which produces this:
```
FIBSEMDataset(biotype='HeLa', alias='Crop 33 / Mito 001', dimensions={'x': 200, 'y': 200, 'z': 200}, ...
```
