import requests
import random
import sys
import re
import math
import datetime
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
DATE_START = '2000-07-26T00:00:00Z'  # если не задано, то '2000-00-00T00:00:00Z'
DATE_FINISH = '2900-00-00T00:00:00Z'  # если не задано, то '2900-00-00T00:00:00Z'


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


def get_pull_requests(url, state, branch, timeout, start, finish):
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
         if start <= pull['created_at'] <= finish]

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


def get_issue(url, state, branch, timeout, start, finish):
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
         if start <= issue['created_at'] <= finish]

        i += 1
    return p, stats


def valid_age(list, number_days):
    """Поиск "старых" элементов списка"""

    n = []
    date_now = datetime.datetime.now().isoformat()
    b1 = re.split(r':', date_now)
    b11 = b1[0].split('T')[0].split('-')
    bb = datetime.date(int(b11[0]), int(b11[1]), int(b11[2]))
    for i in list:
        a1 = re.split(r':', i[1])
        a11 = a1[0].split('T')[0].split('-')
        aa = datetime.date(int(a11[0]), int(a11[1]), int(a11[2]))
        x = math.fabs(int(str(aa - bb).split()[0]))
        if x >= number_days:
            n.append(i)
    return n


def main():
    sys.stdout.write(f"-Sign in GitHub-\n")
    sleep(random.randint(1, 4))
    sign_in = github_resp(url=URL_GIT, login=NAME_PASS,
                          timeout=3, params=''
                          )
    stat_sign_in = sign_in[0]
    sys.stdout.write(stat_sign_in + '\n')

    sys.stdout.write(f"\n-Get commits-\n")
    commits, comm_st = get_commits(url=URL_COMMITS, branch=BRANCH,
                                   since=DATE_START, until=DATE_FINISH, timeout=3)
    if comm_st != 'Success!':
        return sys.stdout.write(f"{comm_st}\n")
    # Считаем коммиты авторов и сортируем по убыванию
    m_commit = Counter(commits).most_common(30)
    # Подготовка данных для построения таблицы
    row_commit = [['Name Author', 'Number commit']]
    [row_commit.append((str(cort[0]), str(cort[1]))) for cort in m_commit]
    # Построение таблицы
    sys.stdout.write(f'Most active author:\n')
    [sys.stdout.write(line + '\n') for line in pretty_table(row_commit, 2)]

    sys.stdout.write(f"\n-Get pulls closed-\n")
    closed_pulls, pulls_stat_cl = get_pull_requests(URL_PULLS, 'closed', BRANCH, 3,
                                                    start=DATE_START, finish=DATE_FINISH
                                                    )
    if pulls_stat_cl != 'Success!':
        return sys.stdout.write(f"{pulls_stat_cl}\n")
    sys.stdout.write(f'\nExamples pulls closed:\n')
    numb_ex_pull = 5  # число выводимых примеров
    [sys.stdout.write(pull[0] + '\n') for index, pull in enumerate(closed_pulls)
     if index < numb_ex_pull]
    sys.stdout.write(f'\nNumber pulls closed = {len(closed_pulls)}\n')

    sys.stdout.write(f"\n-Get pulls open-\n")
    open_pulls, pulls_stat_op = get_pull_requests(URL_PULLS, 'open', BRANCH, 3,
                                                  start=DATE_START, finish=DATE_FINISH
                                                  )
    if pulls_stat_op != 'Success!':
        return sys.stdout.write(f"{pulls_stat_op}\n")
    sys.stdout.write(f'\nExamples pulls open:\n')
    numb_ex_pull = 5  # число выводимых примеров
    [sys.stdout.write(pull[0] + '\n') for index, pull in enumerate(open_pulls)
     if index < numb_ex_pull]
    sys.stdout.write(f'\nNumber pulls open = {len(open_pulls)}\n')

    sys.stdout.write(f'\nExamples old pulls:\n')
    age_pulls = valid_age(open_pulls, 30)
    numb_ex_pull = 5  # число выводимых примеров
    [sys.stdout.write(pull[0] + '\n') for index, pull in enumerate(age_pulls)
     if index < numb_ex_pull]
    sys.stdout.write(f'\nNumber old pulls = {len(age_pulls)}\n')

    sys.stdout.write(f"\n-Get issue closed-\n")
    closed_issue, issue_stat_cl = get_issue(URL_ISSUE, 'closed', BRANCH, 3,
                                            start=DATE_START, finish=DATE_FINISH
                                            )
    if issue_stat_cl != 'Success!':
        return sys.stdout.write(f"{issue_stat_cl}\n")
    sys.stdout.write(f'\nExamples issue closed:\n')
    numb_ex_issue = 5  # число выводимых примеров
    [sys.stdout.write(issue[0] + '\n') for index, issue in enumerate(closed_issue)
     if index < numb_ex_issue]
    sys.stdout.write(f'\nNumber issue closed = {len(closed_issue)}\n')

    sys.stdout.write(f"\n-Get issue open-\n")
    open_issue, issue_stat_op = get_issue(URL_ISSUE, 'open', BRANCH, 3,
                                          start=DATE_START, finish=DATE_FINISH
                                          )
    if issue_stat_op != 'Success!':
        return sys.stdout.write(f"{issue_stat_op}\n")
    sys.stdout.write(f'\nExamples issue open:\n')
    numb_ex_issue = 5  # число выводимых примеров
    [sys.stdout.write(issue[0] + '\n') for index, issue in enumerate(open_issue)
     if index < numb_ex_issue]
    sys.stdout.write(f'\nNumber issue open = {len(open_issue)}\n')

    sys.stdout.write(f'\nExamples old issue:\n')
    age_issue = valid_age(open_issue, 14)
    numb_ex_issue = 5  # число выводимых примеров
    [sys.stdout.write(issue[0] + '\n') for index, issue in enumerate(age_issue)
     if index < numb_ex_issue]
    sys.stdout.write(f'\nNumber old issue = {len(age_issue)}\n')


if __name__ == '__main__':
    main()
