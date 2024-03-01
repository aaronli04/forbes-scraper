import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import concurrent.futures
from helpers import get_hotel, fetch_forbes


def scrape_forbes():
    base_url = 'https://www.forbestravelguide.com'

    forbes_data = fetch_forbes()
    award_winners = forbes_data['awardWinners']

    hotels = []

    for winner in award_winners:
        if winner['propertyType'] == 'HOTEL':
            hotels.append(winner)

    data = []
    for hotel in hotels:
        data_obj = {'name': '', 'forbes_link': '', 'rating': '',
                    'headline': '', 'destination': '', 'country': ''}
        data_obj['name'] = hotel['propertyName']
        data_obj['forbes_link'] = base_url + hotel['propertyURI']
        rating = hotel['propertyRating']
        if rating:
            if rating == 'FOUR_STAR':
                rating = '4'
            elif rating == 'FIVE_STAR':
                rating = '5'
            elif rating == 'RECOMMENDED':
                rating = 'Recommended'
        data_obj['rating'] = rating
        data_obj['headline'] = hotel['propertyHeadline']
        data_obj['destination'] = hotel['destinationName']
        data_obj['country'] = hotel['country']
        data.append(data_obj)

    with concurrent.futures.ThreadPoolExecutor(max_workers=40) as executor:
        results = list(executor.map(get_hotel, data))

    df = pd.DataFrame(results)
    df.to_csv('forbes.csv', index=False)


if __name__ == "__main__":
    scrape_forbes()
