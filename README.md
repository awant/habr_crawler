# habr_crawler
Web crawler of habr.com (Russian collaborative blog about IT, Computer science and anything related to the Internet)

## The goal

The purpose of this repo is to build a missing dataset of articles from the blog for research purposes.
These data (raw) can be used to:

    1. Get more insights on how to prepare an article to attract more attention and to get better rating
    2. Predict articles counters (such as rating, comments, etc) based on a content
    3. [Unsupervised text summarization](https://medium.com/jatana/unsupervised-text-summarization-using-sentence-embeddings-adb15ce83db1)
    4. [Language model/text generation](https://medium.com/phrasee/neural-text-generation-generating-text-using-conditional-language-models-a37b69c7cd4b)
    and more

## The algorithm

The algorithm to collect all articles is simple:

    1. Collect articles from the history. habr allows direct access to a recent history by the url: "https://habr.com/ru/all/all/page{page_idx}". page_idx should be from 1 to 50 and every page has 20 links to articles. So in total you get 1k recent articles.
    2. For each found link download a .html page and collect all links in it startswith "https://habr.com". Do it until all pages are crawled. To understand that a link lead to an article check for {'property': 'og:type', 'content': 'article'} in a 'meta' tag.

The algorithm is pretty straightforward and easy to implement.

I've found out that a delay in 1 second is ok for now to not get banned from the site.


## Scripts

    1. scraper.py
        Downloads articles according to the algorithm
        (parse_paging() - is to dump links from the 1 stage in csv, dump_pages() - download and dump all pages related to articles)
        All data will be in the 'data' folder. The 'data/pages' folder will contain articles by date
    2 prepare_dataset.py
        Collects some useful information from articles and dump it as a .csv file (data/data.csv) for the first insights. Also, dumps only bodies (text without html tags) to a single .json file (data/texts.json) to make dataset more convenient.


## Results

Data can be collected from 2006. 

The number of all articles is enormous and requires too much space. I decided to collect about 10k articles for now (3,7 GB). 

data.csv ~ 30 Mb, texts.json ~ 160 Mb.

## Urls

