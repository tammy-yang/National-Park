import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
import tkinter as tk
from tkinter.constants import *
import tkinter.ttk as ttk

# create cache
CACHE_FILENAME = "NP_data.json"

def open_cache():
    '''
    Creates a cache file if one does not exist and loads the JSON into
    '''
    try:
        cache_file = open(CACHE_FILENAME, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict

def save_cache(cache_dict):
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(CACHE_FILENAME,"w")
    fw.write(dumped_json_cache)
    fw.close()

np_cache = open_cache()


# read in data
national_park = pd.read_csv('National_Parks.csv')
park_code = [code for code in national_park['UNIT_CODE']]
# https://gist.github.com/rogerallen/1583593
us_state_to_abbrev = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",
    "District of Columbia": "DC",
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "United States Minor Outlying Islands": "UM",
    "U.S. Virgin Islands": "VI",
}

# create a tree structure (nested dictionary) to store data
by_state = {}
for state in national_park['STATE']:
    if state not in by_state.keys():
        by_state[state] = []

def categorize_by_state(park):
    '''
    classify parks by state

    Parameters
    ----------
    park : a row of dataframe
    '''
    for state in by_state.keys():
        if park['STATE'] == state:
            by_state[state].append(park['UNIT_CODE'])

attri_dict = {}
def add_dict(park):
    '''build the tree structure with null values

    Parameters
    ----------
    park : dict

    Returns
    -------
    attri_dict : dict
    a nested dictionary with park code as key and attributes as value
    '''
    for val in park.values():
        for code in val:
            attri_dict[code] = {
                'Full Name': '',
                'Description': '',
                'LatLong': '',
                'Address': '',
                'Contact': '',
                'Entrance Fee': '',
                'Operating Hours': '',
                'Activities': '',
                'Campgrounds': ''
            }
    return attri_dict

# create data structure for later use
national_park.apply(categorize_by_state, axis=1)
park_data = add_dict(by_state)
park_data = np_cache
act_list = [] # create a list of all activities
for val in park_data.values():
    for act in val['Activities']:
        if act not in act_list:
            act_list.append(act)
act_list = sorted(act_list)

# PART ONE: NPS API
api_key = '8fLoe0iHK1uwELcOTRO6FxqkoK2sxuwV2yueUAD0'
# url_example = 'https://developer.nps.gov/api/v1/alerts?parkCode=acad,dena&api_key=8fLoe0iHK1uwELcOTRO6FxqkoK2sxuwV2yueUAD0'
activities_url = 'https://developer.nps.gov/api/v1/activities?'
parks_url = 'https://developer.nps.gov/api/v1/parks?'
campgrounds_url = 'https://developer.nps.gov/api/v1/campgrounds?'

# define functions to add attributes to the tree structure
def get_park_attri(url, park_code, api_key, data):
    '''add attributes retrieved from API to the tree structure

    Parameters
    ----------
    url : str
    the url that we want to get data from
    park_code : list
    a list of park codes, used to get each park's data from the url
    api_key : str
    your unique api key
    data : dict
    a nested dictionary that we want to add attributes to

    Returns
    -------
    data : dict
    a nested dictionary with park code as key and attributes as value
    '''
    for code in park_code:
        source = f"{url}parkCode={code}&api_key={api_key}"
        response = requests.get(source)
        result = response.json()
        if code in np_cache.keys():
            return np_cache[code]
        else:
            np_cache[code] = {}
            try:
                np_cache[code]['Full Name'] = result['data'][0]['fullName']
            except:
                pass
            try:
                np_cache[code]['Description'] = result['data'][0]['description']
            except:
                pass
            try:
                np_cache[code]['LatLong'] = result['data'][0]['latLong']
            except:
                pass
            try:
                np_cache[code]['Address'] = result['data'][0]['addresses'][0]
            except:
                pass
            try:
                np_cache[code]['Contact'] = result['data'][0]['contacts']['phoneNumbers'][0]['phoneNumber']
            except:
                pass
            try:
                np_cache[code]['Entrance Fee'] = result['data'][0]['entranceFees']
            except:
                pass
            try:
                np_cache[code]['Operating Hours'] = result['data'][0]['operatingHours'][0]['standardHours']
            except:
                pass
            data[code] = np_cache[code]
            save_cache(np_cache)
    return data

def get_activity_attr(url, park_code, api_key, data):
    '''add activity attributes retrieved from API to the tree structure

    Parameters
    ----------
    url : str
    the url that we want to get data from
    park_code : list
    a list of park codes, used to get each park's data from the url
    api_key : str
    your unique api key
    data : dict
    a nested dictionary that we want to add attributes to

    Returns
    -------
    data : dict
    a nested dictionary with park code as key and attributes as value
    '''
    for code in park_code:
        source = f"{url}parkCode={code}&api_key={api_key}"
        response = requests.get(source)
        result = response.json()
        if code in np_cache.keys():
            return np_cache[code]
        else:
            np_cache[code] = {}
            try:
                activities = result['data']
                np_cache[code]['Activities'] = [act['name'] for act in activities]
            except:
                pass
            data[code] = np_cache[code]
            save_cache(np_cache)
    return data

def get_camp_attr(url, park_code, api_key, data):
    '''add campground attributes retrieved from API to the tree structure

    Parameters
    ----------
    url : str
    the url that we want to get data from
    park_code : list
    a list of park codes, used to get each park's data from the url
    api_key : str
    your unique api key
    data : dict
    a nested dictionary that we want to add attributes to

    Returns
    -------
    data : dict
    a nested dictionary with park code as key and attributes as value
    '''
    for code in park_code:
        source = f"{url}parkCode={code}&api_key={api_key}"
        response = requests.get(source)
        result = response.json()
        camp = result['data']
        if code in np_cache.keys():
            return np_cache[code]
        else:
            np_cache[code] = {}
            try:
                np_cache[code]['Campgrounds'] = [c['name'] for c in camp]
            except:
                pass
            data[code] = np_cache[code]
            save_cache(np_cache)
    return data

# apply function to store data into the tree structure
get_camp_attr(campgrounds_url, park_code, api_key, park_data)
get_park_attri(parks_url, park_code, api_key, park_data)
get_activity_attr(activities_url, park_code, api_key, park_data)


# PART TWO: TYPE (web crawling)
# prase wikipedia and categorized by types
wiki_url = "https://en.wikipedia.org/wiki/List_of_national_parks_of_the_United_States"
response = requests.get(wiki_url)
soup = BeautifulSoup(response.content, "html.parser")
# Find the table containing the national park data
park_table = soup.find("table", {"class": "wikitable"})

br = []    # UNESCO designated Biosphere Reserves (BR)
whs = []   # UNESCO designated World Heritage Sites (WHS)
both = []  # parks designated in both UNESCO programs

def categorize_type(cells, color, type):
    ''' Different types of parks are labeled with different colors on Wikipedia.
    This function categorizes parks by type (based on their colors)

    Parameters
    ----------
    cells : list
    a list of cells in a row
    color : str
    the color of the first cell in a row; used to discriminate the type of park
    type : list
    a list of parks of a certain type. The list that we want to append to

    Returns
    -------
    None
    '''
    if len(cells) > 0 and cells[0].get("bgcolor") == color:
        park_name = cells[0].find("a").text
        location = cells[2].find("a").text
        type.append((park_name, location))

# Loop through each row in the table and classify the park
for row in park_table.find_all("tr"):
    # Find all the cells in the row
    cells = row.find_all("td")
    categorize_type(cells, "#cedff2", br)     # Check if the first cell has bgcolor="#cedff2" (BR)
    categorize_type(cells, "#cfecd2", whs)    # Check if the first cell has bgcolor="#cfecd2" (WHS)
    categorize_type(cells, "#ddcef2", both)    # Check if the first cell has bgcolor="#ddcef2" (both)
# combine to get the full list, and sort by location
br_full = br + both
whs_full = whs + both
br_full = sorted(br_full, key=lambda x: x[1])
whs_full = sorted(whs_full, key=lambda x: x[1])


# PART THREE: USER INTERFACE
window = tk.Tk()
window.title('Info Booth of US National Park')
window.geometry('800x700')
window.resizable(False, False)
title = tk.Label(
    text="Welcome to the info booth of US National Park!",
    font=("Arial", 30))
title.place(x=400, y=50, anchor=CENTER)

# option one - search park by state and activity
instruction = tk.Label(text="Please select the state you want to visit:", font=("Arial", 18))
instruction.place(x=400,y=100,anchor=CENTER)
state_dropdown = ttk.Combobox(window, height=10, width=20, font=('Arial', 15))
state_label = sorted([key for key in us_state_to_abbrev.keys()])
state_dropdown['values'] = state_label
state_dropdown.place(x=400,y=150,anchor=CENTER)
state_dropdown.current(0)
activity_instruction = tk.Label(text="Please select the activity you want to do:", font=("Arial", 18))
activity_instruction.place(x=400,y=200,anchor=CENTER)
activity_dropdown = ttk.Combobox(window, height=10, width=20, font=('Arial', 15))
activity_dropdown['values'] = act_list
activity_dropdown.place(x=400,y=250,anchor=CENTER)

def result_page():
    '''create a new window to display the result of the search'''
    result_page = tk.Toplevel()
    result_page.title("Search Result")
    result_page.geometry("700x600")
    title = tk.Label(result_page, text=f"National Parks in {state_dropdown.get()},\nand the activities they have:", font=("Arial", 20))
    title.pack(pady=20)
    park_filtered_text = tk.Text(result_page, font=("Arial", 15), wrap=WORD, state=DISABLED)
    park_filtered_text.pack(fill=BOTH, expand=1)
    # Create a Scrollbar for the Text widget
    scrollbar = tk.Scrollbar(park_filtered_text)
    scrollbar.pack(side=RIGHT, fill=Y)
    park_filtered_text.config(yscrollcommand=scrollbar.set)
    scrollbar.config(command=park_filtered_text.yview)

    def display_park(state):
        '''display the corresponding parks in the chosen state'''
        park_in_state = by_state[us_state_to_abbrev[state]]
        text = ""
        for park in park_in_state:
            fullname = park_data[park]['Full Name']
            text += f"{fullname} \n "
        return text

    def display_park_activity(park):
        '''display the corresponding parks and their activities in the chosen state'''
        fullname = park_data[park]['Full Name']
        activity = park_data[park]['Activities']
        return f"{fullname}:\n {activity} \n\n "

    def search():
        '''generate the search based on users' input and display the result'''
        state = state_dropdown.get()
        activity = activity_dropdown.get()
        park_in_state = by_state[us_state_to_abbrev[state]]
        if not activity:
            park_filtered_text.config(state=NORMAL)
            park_filtered_text.delete(1.0, END)
            park_filtered_text.insert(END, display_park(state))
            park_filtered_text.config(state=DISABLED)
        else:
            text = ""
            for park in park_in_state:
                if activity in park_data[park]['Activities']:
                    text += f"{display_park_activity(park)}\n"
            if not text: # if text is empty, meaning no park found in the for loop
                park_filtered_text.config(state=NORMAL)
                park_filtered_text.delete(1.0, END)
                park_filtered_text.insert(END, "No parks found with this activity.")
                park_filtered_text.config(state=DISABLED)
            else:
                park_filtered_text.config(state=NORMAL)
                park_filtered_text.delete(1.0, END)
                park_filtered_text.insert(END, text)
                park_filtered_text.config(state=DISABLED)
    search()  # call the search function to display the result in the new window

search_button = tk.Button(window, text="Search 🔍", width=10, height=2, command=lambda: [result_page(), search_page()])
search_button.place(x=400,y=310,anchor=CENTER)

# option two - search by UNESCO type
instruction_2 = tk.Label(text="Or select the type of park you want to visit:", font=("Arial", 20))
instruction_2.place(x=400,y=400,anchor=CENTER)
type_want = tk.IntVar()
type_1 = tk.Radiobutton(window, text="UNESCO Biosphere Reserves", value=1, variable=type_want, font=("Arial",15))
type_1.place(x=400,y=450,anchor=CENTER)
type_2 = tk.Radiobutton(window, text="UNESCO World Heritage Sites", value=2, variable=type_want, font=("Arial",15))
type_2.place(x=400,y=480,anchor=CENTER)
def type_new_page():
    '''create a new window to display the result of the search'''
    type_page = tk.Toplevel()
    type_page.title("Search Result")
    type_page.geometry("400x500")
    title = tk.Label(type_page, font=("Arial", 20))
    title.pack(pady=20)
    type_list = tk.Label(type_page, font=('Arial', 15), wraplength=600)
    type_list.pack(anchor=CENTER)
    def display_list(lst):
        '''display the list of parks'''
        text = ""
        for park in lst:
            text += f"{park[1]}: {park[0]}\n"
        return text

    def get_type():
        '''display the result based on the type of park users want to visit'''
        if type_want.get() == 1:
            title.config(text="UNESCO Biosphere Reserves")
            type_list.config(text=display_list(br_full))
        elif type_want.get() == 2:
            title.config(text="UNESCO World Heritage Sites")
            type_list.config(text=display_list(whs_full))
    get_type() # call the get_type function to display the result in the new window

submit_button = tk.Button(window, text="Submit ✔️", width=10, height=2, command=lambda: [type_new_page(), search_page()])
submit_button.place(x=400,y=550,anchor=CENTER)

exit = tk.Button(window, text='exit ❌', command=window.destroy, activeforeground='gray')
exit.place(x=400,y=650,anchor=CENTER)

# advanced search - choose the park and display information on the new page
def display_park_detail(name):
    '''retrieve data from the tree structure and display the park information based on the park name'''
    park_fullname_list = [name['Full Name'].lower() for name in park_data.values()]
    if name.lower() in park_fullname_list:
        for park in park_data:
            if park_data[park]['Full Name'].lower() == name.lower():
                info = f"{park_data[park]['Full Name']}\n\n" \
                        f"{park_data[park]['Description']}\n\n" \
                        f"Latitude and Longitude: {park_data[park]['LatLong']}\n\n" \
                        f"Address: {park_data[park]['Address']}\n\n" \
                        f"Entrance Fee: {park_data[park]['Entrance Fee']}\n\n" \
                        f"Operating Hours: {park_data[park]['Operating Hours']}\n\n" \
                        f"Activities: {park_data[park]['Activities']}\n\n" \
                        f"Campgrounds: {park_data[park]['Campgrounds']}\n\n" \
                        f"Contact: {park_data[park]['Contact']}\n\n\n" \
                        f"Missing values means no information available."
                return info
    else:
        return "No park found."

def search_page():
    '''create a new pop-up window allowing user to do further search'''
    new_page = tk.Toplevel()
    new_page.title("Search Page")
    new_page.geometry("700x650")
    title_label = tk.Label(new_page, text="Welcome to the search Page!\n If you want to know more about the specificed park,\n please enter the park name in the entry below:\n(Please copy the exact same name from the previous page, thank you.)", font={'Arial', 30})
    title_label.place(x=350, y=100, anchor=CENTER)
    park_entry = tk.Entry(new_page, width=20, font=('Arial', 15))
    park_entry.place(x=350, y=170, anchor=CENTER)
    def search_park():
        '''search the park based on the name entered by the user'''
        park_name = park_entry.get()
        detail.config(state="normal")
        detail.delete("1.0", tk.END)  # clear the text widget before updating it
        detail.insert(tk.END, display_park_detail(park_name))
        detail.config(state="disabled")
    search_button = tk.Button(new_page, text="Search 🔍", width=10, height=2, command=search_park)
    search_button.place(x=350, y=230, anchor=CENTER)
    scrollbar = tk.Scrollbar(new_page)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    detail = tk.Text(new_page, font=('Arial', 15), wrap=tk.WORD, yscrollcommand=scrollbar.set, width=70, height=20, bd=0.5)
    detail.place(x=350, y=450, anchor=CENTER)
    scrollbar.config(command=detail.yview)
    def reset_search():
        '''clear the entry box and search results and reset the search page'''
        park_entry.delete(0, 'end')
        detail.config(state="normal")
        detail.delete("1.0", tk.END)
        detail.config(state="disabled")
    reset_button = tk.Button(new_page, text="Reset", width=10, height=2, command=lambda: reset_search())
    reset_button.pack(side=BOTTOM)

window.mainloop()