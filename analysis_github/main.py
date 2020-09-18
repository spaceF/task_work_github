import requests
import random
from time import sleep
from collections import Counter

# ПАРАМЕТРЫ ВВОДИТЬ С ПАНЕЛИ
URL = ''
NAME_OWNER = 'IgnorantGuru'
NAME_REPOS = 'spacefm'
URL_GIT = 'https://api.github.com'
URL_REP = f'{URL_GIT}/repos/{NAME_OWNER}/{NAME_REPOS}'
URL_COMMITS = f'{URL_REP}/commits'
URL_PULLS = f'{URL_REP}/pulls'
URL_ISSUE = f'{URL_REP}/issues'
NAME_PASS = ('sunday8361@gmail.com', 'cfb71627b6cfae6e5daf0c718b86f59c')
BRANCH = 'master'
DATA_START = '2000-07-26T00:00:00Z'  # если не задано, то '2000-00-00T00:00:00Z'
DATA_FINISH = '2900-00-00T00:00:00Z'  # если не задано, то '2900-00-00T00:00:00Z'


def github_resp(**kwargs):
    """Запрос к GitHub"""

    res = []
    try:
        sleep(random.randint(3, 10))
        r = requests.get(url=f"{kwargs['url']}",
                         auth=kwargs['login'],
                         timeout=kwargs['timeout'],
                         params=kwargs['params'],
                         )
        r.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        res.append(f"Http Error: {errh}")
        return res
    except requests.exceptions.ConnectionError as errc:
        res.append(f"Error Connection: {errc}")
        return res
    except requests.exceptions.Timeout as errt:
        res.append(f"Timeout error: {errt}")
        return res
    except requests.exceptions.RequestException as err:
        res.append(f"Something Else: {err}")
        return res
    else:
        res.append(f'Success!')

        # получаем ссылку на следующую страницу
        link = r.headers.get('link', None)
        if link is not None:
            link_next = [l for l in link.split(',') if 'rel="next"' in l]
            if len(link_next) > 0:
                res.append(int(link_next[0][link_next[0].find("page=")
                                            + 5:link_next[0].find(">")]))
            else:
                res.append(0)
        else:
            res.append(0)

        r.encoding = 'utf-8'
        res.append(r.json())
        return res  # [статус, следующая страница, ответ запроса]


def pretty_table(rows, column_count, column_spacing=4):
    """Построение таблицы"""

    aligned_columns = []
    for column in range(column_count):
        column_data = list(map(lambda row: row[column], rows))
        aligned_columns.append((max(map(len, column_data)) + column_spacing, column_data))

    for row in range(len(rows)):
        aligned_row = map(lambda x: (x[0], x[1][row]), aligned_columns)
        yield ''.join(map(lambda x: x[1] + ' ' * (x[0] - len(x[1])), aligned_row))


def get_pull_requests(url, state, branch, timeout):
    """Получить даты, примеры pull requests
    заданной ветки заданного времени"""

    stats = ''
    p = []
    i = 1  # Итерация страниц
    page = 1  # Флаг наличия следующей страницы
    while page > 0:
        resp_pulls = github_resp(url=url, login='', timeout=timeout,
                                 params={"state": state,
                                         "base": branch,
                                         "page": i
                                         }
                                 )
        stats = resp_pulls[0]
        if stats != 'Success!':
            return p, stats
        page = resp_pulls[1]
        pulls = resp_pulls[2]
        [p.append((pull['title'], pull['created_at'])) for pull in pulls
         if DATA_START <= pull['created_at'] <= DATA_FINISH]

        i += 1
    return p, stats


def get_commits(url, branch, timeout, since, until):
    """Получить авторов коммитов
    заданной ветки заданного времени"""

    stats = ''
    p = []
    i = 1  # Итерация страниц
    page = 1  # Флаг наличия следующей страницы
    while page > 0:
        sleep(random.randint(1, 4))
        resp_commits = github_resp(url=url, login='', timeout=timeout,
                                   params={"sha": branch,
                                           "since": since,
                                           "until": until,
                                           "page": i
                                           }
                                   )
        stats = resp_commits[0]
        if stats != 'Success!':
            return p, stats
        page = resp_commits[1]
        [p.append(com['commit']['author']['name']) for com in resp_commits[2]]
        # Получаем первые 30ть позиций
        if len(p) >= 30:
            return p, stats
        i += 1
    return p, stats


def get_issue(url, state, branch, timeout):
    """Получить даты, примеры issue
    заданной ветки заданного времени"""

    stats = ''
    p = []
    i = 1
    page = 1
    while page > 0:
        sleep(random.randint(1, 4))
        resp_issue = github_resp(url=url, login='', timeout=timeout,
                                 params={"state": state,
                                         "base": branch,
                                         "page": i
                                         }
                                 )
        stats = resp_issue[0]
        if stats != 'Success!':
            return p, stats
        page = resp_issue[1]
        issues = resp_issue[2]
        [p.append((issue['title'], issue['created_at'])) for issue in issues
         if DATA_START <= issue['created_at'] <= DATA_FINISH]

        i += 1
    return p, stats


def main():
    print(f"-Sign in GitHub-")
    sleep(random.randint(1, 4))
    sign_in = github_resp(url=URL_GIT, login=NAME_PASS,
                          timeout=3, params=''
                          )
    stat_sign_in = sign_in[0]
    print(stat_sign_in)

    print(f"\n-Get commits-")
    commits, comm_st = get_commits(url=URL_COMMITS, branch=BRANCH,
                                   since=DATA_START, until=DATA_FINISH, timeout=3)
    if comm_st != 'Success!':
        return print(f"{comm_st}")
    # Считаем коммиты авторов и сортируем по убыванию
    m_commit = Counter(commits).most_common(30)
    # Подготовка данных для построения таблицы
    row_commit = [['Name Author', 'Number commit']]
    [row_commit.append((str(cort[0]), str(cort[1]))) for cort in m_commit]
    # Построение таблицы
    print(f'Most active author')
    [print(line) for line in pretty_table(row_commit, 2)]

    print(f"\nGet pulls closed")
    closed_pulls, pulls_stat_cl = get_pull_requests(URL_PULLS, 'closed', BRANCH, 3)
    if pulls_stat_cl != 'Success!':
        return print(f"{pulls_stat_cl}")
    print(f'\nExamples pulls closed:')
    numb_ex_pull = 5  # число выводимых примеров
    [print(pull[0]) for index, pull in enumerate(closed_pulls)
     if index < numb_ex_pull]
    print(f'\nNumber pulls closed = {len(closed_pulls)}')

    print(f"\nGet pulls open")
    open_pulls, pulls_stat_op = get_pull_requests(URL_PULLS, 'open', BRANCH, 3)
    if pulls_stat_op != 'Success!':
        return print(f"{pulls_stat_op}")
    print(f'\nExamples pulls open:')
    numb_ex_pull = 5  # число выводимых примеров
    [print(pull[0]) for index, pull in enumerate(open_pulls)
     if index < numb_ex_pull]
    print(f'\nNumber pulls open = {len(open_pulls)}')


    print(f"\nGet issue closed")
    closed_issue, issue_stat_cl = get_issue(URL_ISSUE, 'closed', BRANCH, 3)
    if issue_stat_cl != 'Success!':
        return print(f"{issue_stat_cl}")
    print(f'\nExamples issue closed:')
    numb_ex_issue = 5  # число выводимых примеров
    [print(issue[0]) for index, issue in enumerate(closed_issue)
     if index < numb_ex_issue]
    print(f'\nNumber issue closed = {len(closed_issue)}')

    print(f"\nGet issue open")
    open_issue, issue_stat_op = get_issue(URL_ISSUE, 'open', BRANCH, 3)
    if issue_stat_op != 'Success!':
        return print(f"{issue_stat_op}")
    print(f'\nExamples issue open:')
    numb_ex_issue = 5  # число выводимых примеров
    [print(issue[0]) for index, issue in enumerate(open_issue)
     if index < numb_ex_issue]
    print(f'\nNumber issue open = {len(open_issue)}')


if __name__ == '__main__':
    main()
