import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
from tqdm import tqdm
import json
import os
import pickle


class HabrScraper(object):
    habr_url = 'https://habr.com/ru/all/all'
    paging_csv_fp = 'data/paging.csv'
    pages_folder = 'data/pages'
    cache_fp = 'data/cache.pickle'

    @staticmethod
    def download_page(url, throttling=1):
        time.sleep(throttling)
        response = requests.get(url)
        return response.text

    @staticmethod
    def extract_pages_links(html):
        soup = BeautifulSoup(html, 'html.parser')
        return [{'link': link['href'], 'title': link.text} for link in soup.find_all('a', {'class': 'post__title_link'})]

    @staticmethod
    def parse_paging():
        pages = []
        paging_urls = ['{}/page{}'.format(HabrScraper.habr_url, page_idx) for page_idx in range(1, 50+1)]
        for url in tqdm(paging_urls):
            html = HabrScraper.download_page(url)
            pages += HabrScraper.extract_pages_links(html)
        df = pd.DataFrame(pages)
        df.to_csv(HabrScraper.paging_csv_fp, index=False)

    @staticmethod
    def is_article(soup):
        return len(soup.find_all('meta', {'property': 'og:type', 'content': 'article'})) > 0

    @staticmethod
    def get_date_str(soup):
        json_scripts = soup.find_all('script', {'type': 'application/ld+json'})
        if not json_scripts:
            return None
        json_script = json.loads(json_scripts[0].text)
        date_str = json_script.get('datePublished', '')[:10]
        if len(date_str) < 10:
            return None
        return date_str

    @staticmethod
    def get_article_id(url):
        return abs(hash(url)) % (10 ** 8)

    @staticmethod
    def dump_page(html, fp, folder):
        if not os.path.exists(fp):
            if not os.path.exists(folder):
                os.makedirs(folder)
            with open(fp, mode='w') as f:
                f.write(html)

    @staticmethod
    def dump_page_if_article(soup, html):
        if HabrScraper.is_article(soup):
            json_script = soup.find('script', {'type': 'application/ld+json'})
            if not json_script:
                return
            json_script = json.loads(json_script.text)
            url = json_script['mainEntityOfPage'].get('@id')

            date = HabrScraper.get_date_str(soup)
            if date:
                idx = str(HabrScraper.get_article_id(url))
                fp = os.path.join(HabrScraper.pages_folder, date, idx)
                folder = os.path.join(HabrScraper.pages_folder, date)
                HabrScraper.dump_page(html, fp, folder)

    @staticmethod
    def extract_links(url):
        html = HabrScraper.download_page(url)
        soup = BeautifulSoup(html, 'html.parser')
        HabrScraper.dump_page_if_article(soup, html)
        extracted_links = [link.get('href') for link in soup.find_all('a')]
        extracted_links = [x for x in extracted_links if x and ('#' not in x)]
        return list(set([link for link in extracted_links if link.startswith('https://habr.com/ru/') and ('users' not in link)]))

    @staticmethod
    def find_all_pages_links_recursively(link, known_links):
        new_links = [x for x in HabrScraper.extract_links(link) if x not in known_links]
        known_links.update(new_links)
        return new_links, known_links

    @staticmethod
    def init_caches():
        if os.path.exists(HabrScraper.cache_fp):
            with open(HabrScraper.cache_fp, 'rb') as f:
                cache = pickle.load(f)
                links, known_links = cache['links'], cache['known_links']
                links = [x for x in links if x and ('#' not in x) and ('users' not in x)]
                post_links = [x for x in links if '/post/' in x]
                other_links = [x for x in links if '/post/' not in x]
                links = post_links + other_links
            return links, known_links
        else:
            links = list(pd.read_csv(HabrScraper.paging_csv_fp)['link'])
            known_links = set(links)
            return links, known_links

    @staticmethod
    def dump_cache(links, known_links):
        cache = {'links': links, 'known_links': known_links}
        with open(HabrScraper.cache_fp, 'wb') as f:
            pickle.dump(cache, f)

    @staticmethod
    def find_all_pages_links():
        links, known_links = HabrScraper.init_caches()
        iterations = 0
        while len(links) > 0:
            new_links, known_links = HabrScraper.find_all_pages_links_recursively(links[0], known_links)
            links_set = set(links)
            new_links = [x for x in new_links if x not in links_set]
            links = links[1:] + new_links
            iterations += 1
            if iterations % 10 == 0:
                HabrScraper.dump_cache(links, known_links)
            print('iter: {}, links_size: {}, set_size: {}'.format(iterations, len(links), len(known_links)))


def main():
    HabrScraper.find_all_pages_links()


if __name__ == '__main__':
    main()
