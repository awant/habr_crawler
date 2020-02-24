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

1. **scraper.py**
        Downloads articles according to the algorithm
        (parse_paging() - is to dump links from the 1 stage in csv, dump_pages() - download and dump all pages related to articles)
        All data will be in the 'data' folder. The 'data/pages' folder will contain articles by date
2. **prepare_dataset.py**
        Collects some useful information from articles and dump it as a .csv file (data/data.csv) for the first insights. Also, dumps only bodies (text without html tags) to a single .json file (data/texts.json) to make dataset more convenient.


## Results

Data can be collected from 2006. 

The number of all articles is enormous and requires too much space. I decided to collect about 10k articles for now (3,7 GB). 

data.csv ~ 30 Mb, texts.json ~ 160 Mb.

## Urls

1. Habr: https://habr.com/ru/
2. Crawled dataset (data.csv/texts.json and raw .html's): https://drive.google.com/drive/folders/1hGO-JmV8wF9XJulWJT7B-1t9FPGMrDWE?usp=sharing

P.S.: To all pythonists I recommend to try **pipreqs** to build requirements.txt. It is simple to use and doesn't add anything superfluous.

Example of a row from data.csv:

```
{'alphabetic_tokens_count': 1019,
 'article_categories': 'c_ruvds, h_zadachki, h_sql, h_career, f_develop, '
                       'f_management',
 'author_name': 'ru_vds',
 'author_type': 'Person',
 'bookmarks': 354,
 'comments': 74,
 'description': 'Хотя составление SQL-запросов &mdash; это не самое интересное '
                'в работе дата-сайентистов, хорошее понимание SQL чрезвычайно '
                'важно для того, кто хочет преуспеть в любом...',
 'first_5_sentences': 'Хотя составление SQL-запросов — это не самое интересное '
                      'в работе дата-сайентистов, хорошее понимание SQL '
                      'чрезвычайно важно для того, кто хочет преуспеть в любом '
                      'занятии, связанном с обработкой данных. Дело тут в том, '
                      'что SQL — это не только SELECT, FROM и WHERE. Чем '
                      'больше SQL-конструкций знает специалист — тем легче ему '
                      'будет создавать запросы на получение из баз данных '
                      'всего, что ему может понадобиться. Автор статьи, '
                      'перевод которой мы сегодня публикуем, говорит, что она '
                      'направлена на решение двух задач: Изучение механизмов, '
                      'которые выходят за пределы базового знания SQL. '
                      'Рассмотрение нескольких практических задач по работе с '
                      'SQL.',
 'h3_count': 7,
 'href_count': 3,
 'i_count': 0,
 'image': 'https://habrastorage.org/webt/0z/vs/bn/0zvsbnwvpvqk_l_-semjqdqw5fu.jpeg',
 'img_count': 2,
 'last_5_sentences': 'P.S. В нашем маркетплейсе есть Docker-образ с SQL Server '
                     'Express, который устанавливается в один клик. Вы можете '
                     'проверить работу контейнеров на VPS. Всем новым клиентам '
                     'бесплатно предоставляются 3 дня для тестирования. '
                     'Уважаемые читатели! Что вы можете посоветовать тем, кто '
                     'хочет освоить искусство создания SQL-запросов?',
 'lines_count': 159,
 'link': 'https://habr.com/ru/company/ruvds/blog/487878/',
 'max_sentence_len': 578,
 'max_token_len': 21,
 'mean_sentence_len': 173.12962962962962,
 'mean_token_len': 3.9785564853556483,
 'median_sentence_len': 128.0,
 'median_token_len': 2.0,
 'min_sentence_len': 19,
 'modified_date': '2020-02-18',
 'modified_time': '13:20',
 'negative_votes': 17,
 'positive_votes': 45,
 'published_date': '2020-02-18',
 'published_time': '13:20',
 'rating': 28,
 'sentences_count': 54,
 'spoiler_count': 0,
 'tags': 'SQL, разработка',
 'ten_most_common_words': 'id, select, from, таблице, salary, where, employee, '
                          'max, sql, email',
 'text_len': 9442,
 'title': '5 вопросов по SQL, которые часто задают дата-сайентистам на '
          'собеседованиях',
 'tokens_count': 1912,
 'views': 36700,
 'words_count': 774,
 'words_mean': 5.810077519379845}
```