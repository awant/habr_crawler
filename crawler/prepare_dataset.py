import pandas as pd
from bs4 import BeautifulSoup
import json
import re
from nltk.tokenize import sent_tokenize, word_tokenize
import statistics
import string
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from collections import Counter, defaultdict
from pprint import pprint
import os
from tqdm import tqdm
from shutil import copyfile


def get_meta_info(soup):
    json_scripts = soup.find_all('script', {'type': 'application/ld+json'})
    if not json_scripts:
        return
    json_script = json.loads(json_scripts[0].text)
    return {
        'link': json_script['mainEntityOfPage'].get('@id'),
        'title': json_script.get('headline'),
        'published_date': json_script['datePublished'][:10],
        'published_time': json_script['datePublished'][11:16],
        'modified_date': json_script['dateModified'][:10],
        'modified_time': json_script['dateModified'][11:16],
        'author_type': json_script['author'].get('@type'),
        'author_name': json_script['author'].get('name'),
        'description': json_script.get('description'),
        'image': json_script.get('image', [''])[0],
        'article_categories': ', '.join(json_script.get('about', []))
    }


def get_votes(soup):
    labels = soup.find('span', {'class': 'voting-wjt__counter voting-wjt__counter_positive js-score'})
    if not labels:
        return 0, 0
    text = labels['title']
    m = re.search(r'↑(\d+).*↓([-]?\d+)', text)
    if len(m.groups()) < 2:
        return 0, 0
    return int(m.group(1)), int(m.group(2))


def get_bookmarks(soup):
    label = soup.find('span', {'class': 'bookmark__counter js-favs_count'})
    if not label:
        return 0
    return int(label.text)


def get_views(soup):
    label = soup.find('span', {'class': 'post-stats__views-count'})
    if not label:
        return 0
    text = label.text.replace(',', '.')
    try:
        if text[-1] == 'k':
            text = float(text[:-1]) * 1000
        return int(text)
    except ValueError:
        return 0


def get_comments(soup):
    label = soup.find('span', {'class': 'post-stats__comments-count'})
    if not label:
        return 0
    return int(label.text)


def get_target_counters(soup):
    positive_votes, negative_votes = get_votes(soup)

    return {
        'positive_votes': positive_votes,
        'negative_votes': negative_votes,
        'rating': positive_votes - negative_votes,
        'bookmarks': get_bookmarks(soup),
        'views': get_views(soup),
        'comments': get_comments(soup)
    }


def get_body(soup):
    soup_body = soup.find('div', {'class': 'post__body post__body_full'})
    if not soup_body:
        soup_body = soup.find('div', {'class': 'article__body'})
    [x.extract() for x in soup_body.findAll('script')]
    [x.extract() for x in soup_body.findAll('style')]
    return soup_body.text


def get_meta_features(soup):
    soup_body = soup.find('div', {'class': 'post__body post__body_full'})
    if not soup_body:
        soup_body = soup.find('div', {'class': 'article__body'})
    [x.extract() for x in soup_body.findAll('script')]
    [x.extract() for x in soup_body.findAll('style')]

    href_count = len(soup_body.find_all('a', href=True))
    img_count = len([x for x in soup_body.find_all('img')])
    h3_count = len([x for x in soup_body.find_all('h3')])
    i_count = len([x for x in soup_body.find_all('i')])
    spoiler_count = len(soup_body.find_all('div', {'class': 'spoiler'}))
    tags = soup.find('meta', {'name': 'keywords'})
    if tags:
        tags = tags.get('content')
    else:
        tags = soup.find_all('li', {'class': 'inline-list__item inline-list__item_tag'})
        tags = ', '.join([x.text for x in tags])

    return {
        'href_count': href_count,
        'img_count': img_count,
        'tags': tags,
        'h3_count': h3_count,
        'i_count': i_count,
        'spoiler_count': spoiler_count
    }


def get_text_features(soup, language='russian'):
    text = get_body(soup)
    lines = list(filter(None, text.split('\n')))
    joined_lines = ' '.join(lines)
    sentences = sent_tokenize(joined_lines, language)
    sent_lens = [len(x) for x in sentences]
    if not sent_lens:
        sent_lens = [0]

    tokens = word_tokenize(text, language)
    tokens_lens = [len(x) for x in tokens]
    if not tokens_lens:
        tokens_lens = [0]
    alphabetic_tokens = [token.lower() for token in tokens if token.isalpha()]

    table = str.maketrans('', '', string.punctuation)
    stripped_atokens = [w.translate(table) for w in alphabetic_tokens]

    stop_words = set(stopwords.words(language))
    words = [tkn for tkn in stripped_atokens if tkn not in stop_words]

    most_common_words = [x[0] for x in Counter(words).most_common(10)]

    stemmer = SnowballStemmer(language)
    words = [stemmer.stem(word) for word in words]
    words_len = [len(x) for x in words]
    if not words_len:
        words_len = [0]

    return {
        'text_len': len(text),
        'lines_count': len(lines),
        'sentences_count': len(sentences),
        'first_5_sentences': ' '.join(sentences[:5]),
        'last_5_sentences': ' '.join(sentences[-5:]),
        'max_sentence_len': max(sent_lens),
        'min_sentence_len': min(sent_lens),
        'mean_sentence_len': statistics.mean(sent_lens),
        'median_sentence_len': statistics.median(sent_lens),
        'tokens_count': len(tokens),
        'max_token_len': max(tokens_lens),
        'mean_token_len': statistics.mean(tokens_lens),
        'median_token_len': statistics.median(tokens_lens),
        'alphabetic_tokens_count': len(alphabetic_tokens),
        'words_count': len(words),
        'words_mean': statistics.mean(words_len),
        'ten_most_common_words': ', '.join(most_common_words)
    }, text


def parse_html(filepath):
    soup = BeautifulSoup(open(filepath, 'r'), 'html.parser')

    meta = get_meta_info(soup)
    meta_features = get_meta_features(soup)
    counters = get_target_counters(soup)
    text_features, text = get_text_features(soup)

    features = {**meta, **meta_features, **counters, **text_features}
    jsonified_text_raw = {'text': text, 'link': features['link']}

    return features, jsonified_text_raw


def build_dataset(filepath='data/pages', out_df='data/data.csv', out_text='data/texts.json'):
    data = []
    with open(out_text, 'w', encoding="utf-8") as f:
        for (root, dirs, files) in tqdm(os.walk(filepath)):
            for file in files:
                fp = os.path.join(root, file)
                features, jsonified_text_raw = parse_html(fp)
                if features['sentences_count'] > 0 and features['link'] and features['negative_votes'] >= 0:
                    data.append(features)
                    f.write(json.dumps(jsonified_text_raw, ensure_ascii=False)+'\n')

    df = pd.DataFrame(data)
    df.to_csv(out_df, index=False)


def print_stats(filepath='data/pages'):
    s = 0
    data = defaultdict(int)
    for (root, dirs, files) in os.walk(filepath):
        date = root[-10:-6]
        if date.startswith(filepath[:4]):
            continue
        data[date] += len(files)
        s += len(files)
    for date, cnt in sorted(list(data.items()))[::-1]:
        print(date, cnt)
    print(f'sum = {s}')


def test():
    feat, text = parse_html('data/pages/2020-02-18/2384944')
    pprint(feat)


def main():
    # test()
    # print_stats()
    build_dataset()


if __name__ == '__main__':
    main()
