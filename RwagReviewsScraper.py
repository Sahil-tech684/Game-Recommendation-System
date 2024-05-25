import scrapy
import json
import csv
from scrapy.crawler import CrawlerProcess

class Game(scrapy.Spider):
    name = 'GAMEREVIEWS'

    params = {
        'page_size': 40,
        'filter': 'true',
        'comments': 'true',
        'key': 'c542e67aec3a4340908f9de9e86038af'
    }

    base_url = 'https://rawg.io/api/games'

    headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    custom_settings = {
        'FEED_FORMAT': 'json',
        'FEED_URI': 'Data/GamesReviewData.json',
        'LOG_LEVEL': 'ERROR'
    }

    def start_requests(self):
        with open('Data/GamesData.csv', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            games = [{key: row[key] for key in ['id', 'name']} for row in reader]

        for game in games:
            url = f'{self.base_url}/{game["id"]}/reviews?ordering=-created&page=1&page_size=40&key={self.params["key"]}'
            yield scrapy.Request(url=url, headers=self.headers, meta={'game': game, 'page': 1}, callback=self.parse_reviews)

    def parse_reviews(self, response):
        game = response.meta['game']
        page = response.meta['page']
        reviews = json.loads(response.text)['results']

        if page == 1:
            game['reviews'] = []

        for review in reviews:
            game['reviews'].append({'text': review['text']})

        total_count = json.loads(response.text)['count']
        if total_count > 40 * page:
            next_page = page + 1
            next_url = f'{self.base_url}/{game["id"]}/reviews?ordering=-created&page={next_page}&page_size=40&key={self.params["key"]}'
            yield scrapy.Request(url=next_url, headers=self.headers, meta={'game': game, 'page': next_page}, callback=self.parse_reviews)
        else:
            yield game


if __name__ == '__main__':
    process = CrawlerProcess()
    process.crawl(Game)
    process.start()
