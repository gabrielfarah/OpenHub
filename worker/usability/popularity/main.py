import requests
import json
import os

DATA_PATH = os.path.dirname(__file__)
API_URL = ''
API_KEY = ''
POSITIVE = 'positive'
NEGATIVE = 'negative'
NEUTRAL = 'neutral'


def run_test(id, path, repo_db):
    global API_KEY, API_URL

    usr, pwd, API_URL, API_KEY = get_config(DATA_PATH + '/data.json')

    urls = {'comments_url': repo_db['comments_url'], 'issues_url': repo_db['issues_url']}

    issues, watchers, network_count, forks = map(int, (repo_db['open_issues'], repo_db['watchers'], repo_db['network_count'], repo_db['forks']))
    comments, positive, neutral, negative = analyze_sentiment(urls, (usr, pwd))
    stars = get_stargazers_count(repo_db['stargazers_url'], (usr, pwd))
    contribs, commits = get_contrib_and_commit_num('https://api.github.com/repos/'+repo_db['full_name']+'/stats/contributors', (usr, pwd))

    res = sum((contribs*0.15, forks*0.15, watchers*0.2, stars*0.2, commits*0.15, comments*0.05, issues*0.05, positive*0.05))
    print res
    return res


def analyze_sentiment(urls, auth):
    print "Doing sentiment analysis..."
    positive, neutral, negative = 0, 0, 0
    comments = 0

    for key in urls:
        url = urls[key]
        if '{' in url:
            url = url[:url.index('{')]

        res = requests.get(url, auth=auth)

        if 'message' in res and res['message'] == 'Not Found':
            raise Exception('Could not get url' + url)

        for comment in res.json():
            if key == 'comments_url':
                comments += 1
            sent = get_sentiment(comment['body'])
            if sent == POSITIVE:
                positive += 1
            elif sent == NEGATIVE:
                negative += 1
            elif sent == NEUTRAL:
                neutral += 1

    return comments, positive, neutral, negative


def get_stargazers_count(url, auth):
    print "Getting stargazer count..."
    res = requests.get(url, auth=auth).json()
    return len(res)


def get_contrib_and_commit_num(url, auth):
    print "Getting contrib and commit count..."
    res = requests.get(url, auth=auth).json()
    contribs = len(res)
    commits = 0

    for author in res:
        commits += int(author['total'])

    return contribs, commits


def get_sentiment(text):
    if text:
        payload = {'api-key': API_KEY, 'text': text}
        res = requests.get(API_URL, params=payload).json()

        if not res['errors']:
            return res['polarity']
        else:
            print text, res
            raise Exception('Could not analyze sentiment')
    else:
        return None


def get_config(data_path):
    cfg = open(data_path)
    data = json.load(cfg)
    cfg.close()

    return data['GH_USR'], data['GH_PWD'], data['API_URL'], data['API_KEY']

if __name__ == '__main__':
    test = open(DATA_PATH + '/test.json')
    repo_json = json.load(test)
    test.close()

    run_test(None, None, repo_json)
