import json
from scrapy import Request, Spider
from collections import OrderedDict
from csv import DictReader
from copy import deepcopy


class Quora(Spider):
    name = 'quora'

    custom_settings = {
        'FEED_FORMAT': 'csv',
        'FEED_URI': 'Quora 3.csv',
        'DOWNLOAD_DELAY': 0.5
    }

    api_url = 'https://www.quora.com/graphql/gql_para_POST?q=SearchResultsListQuery'
    comment_api = 'https://www.quora.com/graphql/gql_para_POST?q=AnswerCommentLoaderQuery'

    headers = {
        'authority': 'www.quora.com',
        'sec-ch-ua': '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
        'content-type': 'application/json',
        'quora-revision': '1c1d39a54cb07dd58ac163c06b981180b2dc32ad',
        'quora-broadcast-id': 'main-w-chan51-8888-react_pakysyyghtajbngt-lNZl',
        'quora-formkey': '9587271cd5fb92b3afdffbe72ab8198e',
        'quora-canary-revision': 'false',
        'quora-window-id': 'react_pakysyyghtajbngt',
        'sec-ch-ua-platform': '"macOS"',
        'accept': '*/*',
        'origin': 'https://www.quora.com',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.quora.com/search?q=audi',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cookie': 'm-b=KRpWhier8fOupI3PO-vyPw==; m-b_lax=KRpWhier8fOupI3PO-vyPw==; m-b_strict=KRpWhier8fOupI3PO-vyPw==; m-s=YxZscB2jRdpEReH6LrNXYw==; m-ans_frontend_early_version=1b022cd9fb24fa54; m-dynamicFontSize=regular; G_ENABLED_IDPS=google; G_AUTHUSER_H=0; m-theme=light; _scid=92ee584d-fb9e-4f8c-ae36-b7b0a792e282; _gcl_au=1.1.107908203.1634300022; _fbp=fb.1.1634300022989.468313394; _sctr=1|1634238000000; __gads=ID=1db7550c1c137db0:T=1634302396:S=ALNI_MZWmA-T_q2yuQDx4ytZFs_e8d_q-A; m-sa=1; m-lat=s3rN3zMjniz9aQ1I65-Wfw==; m-login=1; m-uid=1638016571; m-b=KRpWhier8fOupI3PO-vyPw==; m-b_lax=KRpWhier8fOupI3PO-vyPw==; m-b_strict=KRpWhier8fOupI3PO-vyPw==; m-s=YxZscB2jRdpEReH6LrNXYw=='
    }
    # NOTE: If scraper stops working you have to login to Quora.com and get the cookies from
    # there and replace then with above cookies to get the latest session


    # Post request data for fetching the posts
    payload = {
        "queryName": "SearchResultsListQuery",
        "extensions": {
            "hash": "f2c225d5c74b2d24d8089d0dff121c8382145dc6595974c69e729b4c7df0139e"
        },
        "variables": {
            "disableSpellCheck": None,
            "resultType": "all_types",
            "author": None,
            "time": "all_times",
            "first": 10,
            "tribeId": None
        }
    }

    # Post request data for fetching the comments
    comment_payload = {
        "queryName": "AnswerCommentLoaderQuery",
        "extensions": {
            "hash": "b447ea32458240bba227a6ef8b1f9fee3d5689cb3828493a67b0943f9a334978"
        },
        "variables": {
            "aid": 311246114,
            "first": 5
        }
    }

    def start_requests(self):
        # Reading keywords from my keyword file and making an api request
        for row in DictReader(open('keyword.csv')):
            payload = deepcopy(self.payload)
            payload['variables']['query'] = row['keyword']
            meta = {'keyword': row['keyword'], 'dont_merge_cookies': True}
            yield Request(self.api_url, self.parse_post, meta=meta,
                          headers=self.headers, method='POST', body=json.dumps(payload))

    def parse_post(self, response):
        # Parsing the api data response and extracting required information
        data = json.loads(response.text)['data'].get('searchConnection', {})
        for post in data['edges']:
            try:
                aid = post['node']['previewAnswer']['aid']
            except:
                continue
            payload = deepcopy(self.comment_payload)
            payload['variables']['aid'] = aid
            title = self.get_value(post['node']['question']['title'])
            post_text = self.get_value(post['node']['previewAnswer']['content'])
            post_url = response.urljoin(post['node']['question']['url'])
            item = OrderedDict()
            item['keyword'] = response.meta['keyword']
            item['Post Title'] = title
            item['Post Text'] = post_text
            item['Post Url'] = post_url
            for page in range(1, 6):
                item['Comment {}'.format(page)] = ''
            meta = deepcopy(response.meta)
            meta['item'] = item
            # Making a request for getting the comments from post url.
            yield Request(self.comment_api, self.parse_comments, meta=meta,
                          headers=self.headers, method='POST', body=json.dumps(payload))

        if not data['pageInfo']['hasNextPage']:
            return

        # Next page requests limit to first 5 pages to get around 100 records per keyword
        next_cursor = data['pageInfo']['endCursor']
        if int(next_cursor) > 139:
            return
        payload = json.loads(response.request.body)
        payload['variables']['after'] = next_cursor
        yield Request(self.api_url, self.parse_post, meta=response.meta,
                      headers=self.headers, method='POST', body=json.dumps(payload))

    def parse_comments(self, response):
        # Extracting the first 5 comments from the post.
        item = response.meta['item']
        try:
            comments = json.loads(response.text)['data']['answer']['allCommentsConnection']['edges']
        except:
            comments = []

        for index, comment in enumerate(comments):
            if comment['node']['content']:
                item['Comment {}'.format(index + 1)] = self.get_value(comment['node']['content'])

        yield item

    def get_value(self, data):
        sections = json.loads(data).get('sections', [])
        answer = []
        for sec in sections:
            for span in sec['spans']:
                answer.append(span['text'])
        return ' '.join(answer)
