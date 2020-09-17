import requests
import random
from time import sleep
from collections import Counter

# ПАРАМЕТРЫ ВВОДИТЬ С ПАНЕЛИ
URL = ''
NAME_OWNER = 'nedbat'
NAME_REPOS = 'coveragepy'
URL_GIT = 'https://api.github.com'
URL_REP = f'{URL_GIT}/repos/{NAME_OWNER}/{NAME_REPOS}'
URL_COMMITS = f'{URL_REP}/commits'
URL_PULLS = f'{URL_REP}/pulls'
NAME_PASS = ('sunday8361@gmail.com', 'cfb71627b6cfae6e5daf0c718b86f59c')
BRANCH = 'master'
DATA_START = '2000-00-00T00:00:00Z'  # если не задано, то '2000-00-00T00:00:00Z'
DATA_FINISH = ''  # если не задано, то ''
NUMBER_COMMIT = 30


def respons(**kwargs):
    """Запрос к GitHub"""
    try:
        r = requests.get(url=kwargs['url'],
                         auth=kwargs['login'],
                         timeout=kwargs['timeout'],
                         params=kwargs['params'],
                         )
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print(f"Http Error: {errh}")
    except requests.exceptions.ConnectionError as errc:
        print(f"Error Connection: {errc}")
    except requests.exceptions.Timeout as errt:
        print(f"Timeout error: {errt}")
    except requests.exceptions.RequestException as err:
        print(f"Somthing Else: {err}")
    else:

        # получаем ссылку на следующую страницу
        res = []
        link = r.headers.get('link', None)
        if link is not None:
            link_next = [l for l in link.split(',') if 'rel="next"' in l]
            if len(link_next) > 0:
                res.append(int(link_next[0][link_next[0].find("page=")
                                            + 5:link_next[0].find(">")]))
        else:
            res.append(0)

        r.encoding = 'utf-8'
        res.append(r.json())
        return res


def pretty_table(rows, column_count, column_spacing=4):
    """Построение таблицы"""
    aligned_columns = []
    for column in range(column_count):
        column_data = list(map(lambda row: row[column], rows))
        aligned_columns.append((max(map(len, column_data)) + column_spacing, column_data))

    for row in range(len(rows)):
        aligned_row = map(lambda x: (x[0], x[1][row]), aligned_columns)
        yield ''.join(map(lambda x: x[1] + ' ' * (x[0] - len(x[1])), aligned_row))


if __name__ == '__main__':
    print(f"Sign in GitHub")
    sleep(random.randint(1, 4))
    sign_in = respons(url=URL_GIT, login=NAME_PASS,
                      timeout=3, params=''
                      )

    print(f"Get commits")
    sleep(random.randint(1, 4))
    resp_commits = respons(url=URL_COMMITS, login='', timeout=3,
                           params={"sha": BRANCH,
                                   "since": DATA_START,
                                   "until": DATA_FINISH}
                           )
    all_commits = resp_commits[1]
    # Парсим авторов коммитов
    most_commit = []
    for i in range(0, NUMBER_COMMIT - 1, 1):
        try:
            most_commit.append(
                all_commits[i]['commit']['author']['name']
            )
        except IndexError:
            print(f'All names of the commit authors collected!\n\n')
            break
    # Считаем коммиты авторов и сортируем по убыванию
    m_commit = Counter(most_commit).most_common(30)
    # Подготовка данных для построения таблицы
    row_commit = [['Name Author', 'Number commit']]
    for cort in m_commit:
        try:
            row_commit.append((str(cort[0]), str(cort[1])))
        except IndexError:
            print(f'Index Error\n')
            break
    # print(most_commit)
    # Построение таблицы
    print(f'Most active author')
    for line in pretty_table(row_commit, 2):
        print(line)

    print(f"\nGet pulls closed")
    closed_pulls = []
    page = 1
    while page > 0:
        sleep(random.randint(1, 4))
        resp_pulls = respons(url=URL_PULLS, login='', timeout=3,
                             params={"state": "closed",
                                     "base": BRANCH}
                             )
        page = resp_pulls[0]
        closed_pulls.append(resp_pulls[1])
    print(closed_pulls)

    print(f"\nGet pulls open")
    open_pulls = []
    page = 1
    while page > 0:
        sleep(random.randint(1, 4))
        resp_pulls = respons(url=URL_PULLS, login='', timeout=3,
                             params={"state": "open",
                                     "base": BRANCH}
                             )
        page = resp_pulls[0]
        open_pulls.append(resp_pulls[1])
    print(open_pulls)

