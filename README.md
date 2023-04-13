# US National Park Information Search

The US National Park Information Search is a tool that allows users to input their needs and get the corresponding results.\
This code provides information about national parks in the United States using the National Park Service API and web crawling. The information is categorized and stored in a nested dictionary structure.

## Requirements
This code needs the following package to run:
* requests
* BeautifulSoup
* pandas
* json
* tkinter

## Data Structure
The project use tree structure to store the data. Please see NP_data.json file to access tree structure data. \
{CA: ['YOSE', 'CABR', 'CHIS', 'DEVA', 'GOGA', 'FOPO', 'EUON', ……]} \
{'YOSE': {'Full Name': 'Yosemite National Park', 'LatLong': 'lat:37.84883288, long:-119.5571873',……}} \
The UNIT_CODE would serve as the unique identifier and a key to match between data.


## Usage
1. Set up your API key by replacing the placeholder api_key in the code with your unique key. (You can register one at https://www.nps.gov/subjects/developer/api-documentation.htm#/)
2. Run the code.
3. The information about national parks will be stored in a nested dictionary structure named park_data.

## User Instruction
1. Select to search by location and activity or by UNESCO type.
2. Enter your preference.
3. Click the "Search" or "Submit" button to execute the search.
4. The result will display in a new window.
5. If you want to know more about a desired park, paste the exact same name to another pop-up search window.
6. Press the "Exit" button to leave the search tool.
7. Use "Reset" or re-submit to generate a new search.

## Notes
* The nested dictionary structure is stored in the park_data dictionary.
* The np_cache dictionary is used to cache API responses for faster retrieval.
