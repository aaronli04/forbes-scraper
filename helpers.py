import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException


def extract_soup_with_selenium(link):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    driver = webdriver.Chrome(options=options)
    driver.get(link)

    try:
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')
    finally:
        driver.quit()
        return soup


def fetch_forbes():
    url = "https://www.forbestravelguide.com/award-winners.json?format=json"
    response = requests.get(url)
    data = {}

    if response.status_code == 200:
        data = response.json()

    return data


def replace_newlines_with_space(text):
    return text.replace('\n', ' ')


def get_hotel(obj):
    base_url = 'https://www.forbestravelguide.com'

    link = obj['forbes_link']
    soup = extract_soup_with_selenium(link)

    name = obj['name']
    forbes_link = obj['forbes_link']
    rating = obj['rating']
    headline = obj['headline']
    destination = obj['destination']
    country = obj['country']
    description = ''
    inspector_highlights = ''
    tips = ''
    look = ''
    rooms = ''
    restaurants = ''
    spas = ''
    amenities = []
    address = ''
    phone_number = ''
    airports = []
    stories = []
    at_this_hotel = []
    travel_guide = ''

    sections_to_extract = ["Our Inspector's Highlights", "The Look",
                           "Things to Know", "The Rooms", "The Restaurants", "The Spa", "Amenities"]

    description_elem = soup.find('span', class_='fullContent hidden')
    if description_elem:
        description = description_elem.text.strip()

    info_wrapper = soup.find('div', class_='infoBlockWrap')
    if info_wrapper:
        info_elems = info_wrapper.find_all(
            'div', class_='infoBlock contentBlock')
        if info_elems and len(info_elems) > 0:
            for info_elem in info_elems:
                title = info_elem.find(
                    'div', class_="infoBlockTitle").text.strip()
                content = info_elem.find('div', class_='accordionContent')
                if content:
                    items = [item.get_text(strip=True)
                             for item in content.find_all('li')]
                    if title in sections_to_extract:
                        if title == "Our Inspector's Highlights":
                            inspector_highlights = items
                        elif title == "The Look":
                            look = items
                        elif title == "Things to Know":
                            tips = items
                        elif title == "The Rooms":
                            rooms = items
                        elif title == "The Restaurants":
                            restaurants = items
                        elif title == "The Spa":
                            spas = items
                        elif title == "Amenities":
                            amenities_elems = info_elem.find_all(
                                'div', class_='amenityList col-xs-12 col-sm-6 col-md-6')
                            for elem in amenities_elems:
                                amenities.append(elem.text.strip())

    location_elem = soup.find('div', class_="propGettingThere")
    if location_elem:
        address_elem = location_elem.find('div', class_="propAddress")
        if address_elem:
            address = address_elem.text.strip()

        phone_elem = location_elem.find('div', class_="propContact")
        if phone_elem:
            number_elem = phone_elem.find('span', class_="contactText")
            if number_elem:
                phone_number = number_elem.text.strip()

        airport_elem = location_elem.find('div', class_="airportList")
        if airport_elem:
            airports_elem = airport_elem.find_all('a')
            for elem in airports_elem:
                airport = {'name': '', 'directions': ''}
                airport['name'] = elem.text.strip()
                airport['directions'] = elem.get('href')
                airports.append(airport)

    guide_elem = soup.find('div', class_="row contentBlock aCenter")
    if guide_elem:
        guide_link_elem = guide_elem.find('a')
        if guide_link_elem:
            travel_guide = base_url + guide_link_elem.get('href')

    story_blocks = soup.find_all('div', class_='storyBlock')
    if story_blocks and len(story_blocks) > 0:
        for story_block in story_blocks:
            story_content = story_block.find('div', class_="thumbTitle")
            if story_content:
                story = {'name': '', 'link': ''}
                link_elem = story_content.find('a')
                story['name'] = link_elem.text.strip()
                story['link'] = link_elem['href']
                stories.append(story)

    item_blocks_container = soup.find('div', class_='atThisPropList')
    if item_blocks_container:
        hotel_blocks = item_blocks_container.find_all('div')
        for hotel_block in hotel_blocks:
            hotel_content = hotel_block.find('div', class_="thumbTitle")
            if hotel_content:
                feature = {'name': '', 'link': ''}
                feature_elem = hotel_content.find('a')
                feature['name'] = feature_elem.text.strip()
                feature['link'] = base_url + feature_elem.get('href')
                at_this_hotel.append(feature)

    description = replace_newlines_with_space(description)
    inspector_highlights = [replace_newlines_with_space(
        highlight) for highlight in inspector_highlights]
    tips = [replace_newlines_with_space(tip) for tip in tips]
    look = [replace_newlines_with_space(item) for item in look]
    rooms = [replace_newlines_with_space(item) for item in rooms]
    restaurants = [replace_newlines_with_space(item) for item in restaurants]
    spas = [replace_newlines_with_space(item) for item in spas]
    amenities = [replace_newlines_with_space(item) for item in amenities]
    address = replace_newlines_with_space(address)

    result = {
        'name': name,
        'forbes_link': forbes_link,
        'rating': rating,
        'headline': headline,
        'destination': destination,
        'country': country,
        'description': description,
        'inspector_highlights': inspector_highlights,
        'tips': tips,
        'look': look,
        'rooms': rooms,
        'restaurants': restaurants,
        'spas': spas,
        'amenities': amenities,
        'address': address,
        'phone_number': phone_number,
        'airports': airports,
        'stories': stories,
        'at_this_hotel': at_this_hotel,
        'travel_guide': travel_guide
    }

    return result
