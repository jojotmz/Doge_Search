import json
from scrapy import Request, Spider
from collections import OrderedDict
from csv import DictReader
from copy import deepcopy


class Reddit(Spider):
    name = 'reddit'

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'Reddit.csv',
        'DOWNLOAD_DELAY': 0.3
    }

    api_url = 'https://gateway.reddit.com/desktopapi/v1/search?rtj=only&include=structuredStyles,' \
              'prefsSubreddit&q={}&sort=relevance&t=all&type=link,sr,user&b=true'

    def start_requests(self):
        # Reading keywords from the file and making an api request
        for row in DictReader(open('keyword.csv')):
            url = self.api_url.format(row['keyword'])
            meta = {'keyword': row['keyword']}
            yield Request(url, self.parse_post, meta=meta)

    def parse_post(self, response):
        # Parsing the api data response and extracting the required information
        data = json.loads(response.text)
        for post in data['posts'].values():
            item = OrderedDict()
            item['Keyword'] = response.meta['keyword']
            item['Post Text'] = post['title']
            item['Post Url'] = post['permalink']
            for page in range(1, 6):
                item['Comment {}'.format(page)] = ''
                meta = {'item': item}
                # Making a request to obtain the comments from post url.
                yield response.follow(item['Post Url'], self.parse_comments, meta=meta)

        # Next page requests limit to first 5 page
        pagination_limit = response.meta.get('pagination_limit', 0)
        if pagination_limit >= 5:
            return

        if data['tokens']['posts']:
            meta = deepcopy(response.meta)
            meta['pagination_limit'] = pagination_limit + 1
            url = '{}&after={}'.format(response.url, data['tokens']['posts'])
            yield Request(url, self.parse_post, meta=meta)

    def parse_comments(self, response):
        # Extracting the first 5 comments from each post.
        item = response.meta['item']
        for index, comment in enumerate(response.css('._1YCqQVO-9r-Up6QPB9H6_4 > div')[:5]):
            item['Comment {}'.format(index + 1)] = '\n'.join(comment.css('p::text').getall())
        yield item
