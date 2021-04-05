#################################
##### Name: Yixuan Jia
##### Uniqname: jiayx
#################################

from bs4 import BeautifulSoup
import requests
import json
import secrets # file that contains your API key
import time


class NationalSite:
    '''a national site

    Instance Attributes
    -------------------
    category: string
        the category of a national site (e.g. 'National Park', '')
        some sites have blank category.
    
    name: string
        the name of a national site (e.g. 'Isle Royale')

    address: string
        the city and state of a national site (e.g. 'Houghton, MI')

    zipcode: string
        the zip-code of a national site (e.g. '49931', '82190-0168')

    phone: string
        the phone of a national site (e.g. '(616) 319-7906', '307-344-7381')
    '''
    def __init__(self, category, name, address, zipcode, phone):
        self.category = category
        self.name = name
        self.address = address
        self.zipcode = zipcode
        self.phone = phone
    
    def info(self):
        info_str = self.name + ' (' + self.category + '): ' + self.address + ' ' + self.zipcode
        return info_str
    
    pass


def build_state_url_dict():
    ''' Make a dictionary that maps state name to state page url from "https://www.nps.gov"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a state name and value is the url
        e.g. {'michigan':'https://www.nps.gov/state/mi/index.htm', ...}
    '''
    state_url_dict = {}
    nps_BASE_URL = 'https://www.nps.gov'
    nps_INDEX_URL = nps_BASE_URL + '/index.htm'

    # making url request using cache
    CACHE_DICT = load_cache()
    nps_response = make_url_request_using_cache(nps_INDEX_URL, CACHE_DICT)

    state_soup = BeautifulSoup(nps_response, 'html.parser')
    state_list_parent = state_soup.find('ul', class_="dropdown-menu SearchBar-keywordSearch")
    state_list = state_list_parent.find_all('a', recursive=True)
    
    for state in state_list:
        state_name = state.text.lower()
        state_url = nps_BASE_URL + state['href']
        state_url_dict[state_name] = state_url
    
    return state_url_dict
       

def get_site_instance(site_url):
    '''Make an instances from a national site URL.
    
    Parameters
    ----------
    site_url: string
        The URL for a national site page in nps.gov
    
    Returns
    -------
    instance
        a national site instance
    '''
    # site_response = requests.get(site_url)
    # making url request using cache
    CACHE_DICT = load_cache()
    site_response = make_url_request_using_cache(site_url, CACHE_DICT)

    site_soup = BeautifulSoup(site_response, 'html.parser')
    # print(site_soup.prettify())
    site_category = site_soup.find('span', class_ = 'Hero-designation').text.strip()
    site_name = site_soup.find('div', class_ = "Hero-titleContainer clearfix").find('a').text.strip()
    site_address_locatily = site_soup.find('span', itemprop = 'addressLocality').text.strip()
    site_address_region = site_soup.find('span', itemprop = 'addressRegion').text.strip()
    site_address = site_address_locatily + ', ' + site_address_region.strip()
    site_zipcode = site_soup.find('span', itemprop = 'postalCode').text.strip()
    site_phone = site_soup.find('span', itemprop = 'telephone').text.strip()
    
    site_instance = NationalSite(site_category, site_name, site_address, site_zipcode, site_phone)
    
    return site_instance
    


def get_sites_for_state(state_url):
    '''Make a list of national site instances from a state URL.
    
    Parameters
    ----------
    state_url: string
        The URL for a state page in nps.gov
    
    Returns
    -------
    list
        a list of national site instances
    '''
    site_url_list = []
    site_instance_list = []
    
    # state_response = requests.get(state_url)
    # making url request using cache
    CACHE_DICT = load_cache()
    state_response = make_url_request_using_cache(state_url, CACHE_DICT)
    state_soup = BeautifulSoup(state_response, 'html.parser')
    site_url_li_parent = state_soup.find('ul', id = 'list_parks')
    # print(site_url_li_parent.prettify())
    site_url_li = site_url_li_parent.find_all('li', class_ = 'clearfix')

    for site in site_url_li:
        site_url_href = site.find('h3').find('a')['href'].strip()
        # print(site_url_href)
        site_url = 'https://www.nps.gov' + site_url_href + 'index.htm'
        site_url_list.append(site_url)
        site_instance = get_site_instance(site_url)
        site_instance_list.append(site_instance)
    
    return site_instance_list


def get_nearby_places(site_object):
    '''Obtain API data from MapQuest API.
    
    Parameters
    ----------
    site_object: object
        an instance of a national site
    
    Returns
    -------
    dict
        a converted API return from MapQuest API
    '''
    BASE_URL = 'https://www.mapquestapi.com/search/v2/radius?'
    query_url = 'origin=' + f'{site_object.zipcode}' + '&radius=10&maxMatches=10&ambiguities=ignore&outFormat=json&key='
    url = BASE_URL + query_url + secrets.API_KEY
    
    # response = requests.get(url)
    # making url request using cache
    CACHE_DICT = load_cache()
    response = make_url_request_using_cache(url, CACHE_DICT)
    resp_data = json.loads(response)
    # resp_data = response.json()
    return resp_data


# Following three functions are added for caching
def load_cache():
    '''Loading cache file if it exists or set up a new one if not.
    
    Parameters
    ----------
    None
    
    Returns
    -------
    dict
        a cache dictionary
    '''
    try:
        cache_file = open('cache_proj2.json', 'r')
        cache_file_contents = cache_file.read()
        cache = json.loads(cache_file_contents)
        cache_file.close()
    except:
        cache = {}
    return cache

def save_cache(cache):
    '''Saving cache file.
    
    Parameters
    ----------
    cache: dictionary
        a dictionary to be written into the cache file
    
    Returns
    -------
    None
    '''
    cache_file = open('cache_proj2.json', 'w')
    contents_to_write = json.dumps(cache)
    cache_file.write(contents_to_write)
    cache_file.close()

def make_url_request_using_cache(url, cache):
    '''Making a url using cache.
    
    Parameters
    ----------
    url: string
        a url to be requested upon
    
    cache: dictionary
        a dictionary with visited urls as keys and responses as values 
    
    Returns
    -------
    string
        a url string made with cache
    '''
    if (url in cache.keys()):
        print("Using cache")
        return cache[url]
    else:
        print("Fetching")
        time.sleep(1)
        response = requests.get(url)
        cache[url] = response.text
        save_cache(cache)
        return cache[url]

def step_4_nearby_places_print(resp_data):
    '''Printing a list of infomation of nearby places in detail.
    
    Parameters
    ----------
    resp_data: dict
        a json dict to be parsed 
    
    Returns
    -------
    None
    '''
    # searchResults_print_list = []
    searchResults_list = resp_data['searchResults']
    for searchResults in searchResults_list:
        nearby_place_name = searchResults['name'].strip()
        if searchResults['fields']['group_sic_code_name_ext'] != '':
            nearby_place_category = searchResults['fields']['group_sic_code_name_ext'].strip()
        else:
            nearby_place_category = 'no category'
        if searchResults['fields']['address'] != '':
            nearby_place_address = searchResults['fields']['address'].strip()
        else:
            nearby_place_address = 'no address'
        if searchResults['fields']['city'] != '':
            nearby_place_city = searchResults['fields']['city'].strip()
        else:
            nearby_place_city = 'no city'
        searchResults_info = '- ' + nearby_place_name + ' (' + nearby_place_category + '): ' + nearby_place_address + ', ' + nearby_place_city
        # searchResults_print_list.append(searchResults_info)
        print(searchResults_info)
    print('')


if __name__ == "__main__":
    CACHE_DICT = load_cache()
    state_url_dict = build_state_url_dict()

    while True:
        # set up step 3 to 1 flag
        step_3_to_1_flag = False

        # step 1
        state_name_input = input("Enter a state name (e.g. Michigan, michigan) or \"exit\"\n: ")
        state_name_raw = state_name_input.strip().lower()
        if state_name_raw == "exit":
            quit()
        elif state_name_raw in state_url_dict.keys():
            state_name = state_name_raw
        else:
            print("[Error] Enter proper state name\n")
            continue

        # step 2
        site_instance_list = get_sites_for_state(state_url_dict[state_name])
        site_list_str = 'List of national sites in ' + f'{state_name}'
        print('-' * len(site_list_str))
        print(site_list_str)
        print('-' * len(site_list_str))

        site_index = 1
        for site_instance in site_instance_list:
            print('[' + str(site_index) + ']' + site_instance.info())
            site_index = site_index + 1
        print('')

        # step 3
        while(True):
            print('-' * len(site_list_str))
            site_num_input = input("Choose the number for detail search or \"exit\" or \"back\"\n: ")
            site_num_raw = site_num_input.strip()
            if site_num_raw == 'back':
                step_3_to_1_flag = True
                break

            elif site_num_input == 'exit':
                quit()
            
            else:
                try:
                    site_num = int(site_num_raw)
                except:
                    print('[Error] Invalid input\n')
                
                if site_num > len(site_instance_list) or site_num <= 0:
                    print('[Error] Invalid input\n')
                # step 4
                else:
                    resp_data = get_nearby_places(site_instance_list[site_num - 1])
                    print('-' * len(site_list_str))
                    print('Places near ' + f'{site_instance_list[site_num - 1].name}')
                    print('-' * len(site_list_str))
                    step_4_nearby_places_print(resp_data)
        

        # check if the user is going back to step 1
        if step_3_to_1_flag == True:
            continue