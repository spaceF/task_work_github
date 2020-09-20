import requests
import sys
import datetime
from getpass import getpass
from time import sleep
from collections import Counter
from math import fabs
from random import randint
from re import split


def github_resp(**kwargs):
    """Запрос к GitHub"""

    res = []
    try:
        sleep(randint(3, 10))
        r = requests.get(url=f"{kwargs['url']}",
                         auth=kwargs['login'],
                         timeout=kwargs['timeout'],
                         params=kwargs['params'],
                         )
        r.raise_for_status()
    except requests.exceptions.HTTPError as err_h:
        res.append(f"Http Error: {err_h}")
        return res
    except requests.exceptions.ConnectionError as err_c:
        res.append(f"Error Connection: {err_c}")
        return res
    except requests.exceptions.Timeout as err_t:
        res.append(f"Timeout error: {err_t}")
        return res
    except requests.exceptions.RequestException as err:
        res.append(f"Something Else: {err}")
        return res
    else:
        res.append(f'Success!')

        # получаем ссылку на следующую страницу
        link = r.headers.get('link', None)
        if link is not None:
            link_next = [l_n for l_n in link.split(',') if 'rel="next"' in l_n]
            if len(link_next) > 0:
                res.append(int(link_next[0][link_next[0].find("page=")
                                            + 5:link_next[0].find(">")]))
            else:
                # ссылки на след. страницу нет
                res.append(0)
        else:
            # ссылки на след. страницу нет
            res.append(0)
        r.encoding = 'utf-8'
        res.append(r.json())
        return res  # [статус, следующая страница, ответ запроса]


def pretty_table(rows, column_count, column_spacing=4):
    """Построение таблицы"""

    aligned_columns = []
    for column in range(column_count):
        column_data = list(map(lambda row_: row_[column], rows))
        aligned_columns.append((max(map(len, column_data)) + column_spacing, column_data))

    for row in range(len(rows)):
        aligned_row = map(lambda x: (x[0], x[1][row]), aligned_columns)
        yield ''.join(map(lambda x: x[1] + ' ' * (x[0] - len(x[1])), aligned_row))


def get(url, state, branch, timeout, start, finish):
    """Получить даты, примеры заданной
    ветки заданного времени"""

    stats = ''
    p = []
    i = 1  # Итерация страниц
    page = 1  # Флаг наличия следующей страницы
    while page > 0:
        resp = github_resp(url=url, login='', timeout=timeout,
                           params={"state": state,
                                   "base": branch,
                                   "page": i
                                   }
                           )
        stats = resp[0]
        if stats != 'Success!':
            return p, stats
        page = resp[1]
        [p.append((r['title'], r['created_at'])) for r in resp[2]
         if start <= r['created_at'] <= finish]

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


def valid_age(list_, number_days):
    """Поиск "старых" элементов списка"""

    n = []
    date_now = datetime.datetime.now().isoformat()
    b1 = split(r':', date_now)
    b11 = b1[0].split('T')[0].split('-')
    bb = datetime.date(int(b11[0]), int(b11[1]), int(b11[2]))
    for i in list_:
        a1 = split(r':', i[1])
        a11 = a1[0].split('T')[0].split('-')
        aa = datetime.date(int(a11[0]), int(a11[1]), int(a11[2]))
        x = fabs(int(str(aa - bb).split()[0]))
        if x >= number_days:
            n.append(i)
    return n


def is_not_blank(s):
    """ Отслеживаем пустое
    значение и пробел"""

    return bool(s and s.strip())


def main():
    # ПАРАМЕТРЫ
    url = input(f'\nСсылка на репозиторий: ')
    if not is_not_blank(url):
        return sys.stdout.write(f'\nСсылка на репозиторий не найдена\n')
    name_owner = url.split('/')[3]
    name_repos = url.split('/')[4]
    url_git = 'https://api.github.com'
    url_rep = f'{url_git}/repos/{name_owner}/{name_repos}'
    url_commits = f'{url_rep}/commits'
    url_pulls = f'{url_rep}/pulls'
    url_issue = f'{url_rep}/issues'

    mail_git = input(f'\nПочта аккаунта Github: ')
    if not is_not_blank(mail_git):
        return sys.stdout.write(f'\nПочта не найдена\n')
    pass_git = getpass(f'\nПароль: ')
    if not is_not_blank(pass_git):
        return sys.stdout.write(f'\nПароль не найден\n')
    mail_pass = (mail_git, pass_git)

    branch = input(f'\nВетвь для анализа: ')
    if not is_not_blank(branch):
        sys.stdout.write(f'\nВетка не найдена. '
                         'По умолчанию устанавливается master\n')
        branch = 'master'

    date_start = input(f'\nДата начала анализа (ГГ-ММ-ДД): ') + 'T00:00:00Z'
    date_finish = input(f'\nДата окончания анализа (ГГ-ММ-ДД): ') + 'T00:00:00Z'
    if date_start == 'T00:00:00Z':
        date_start = '2000-00-00T00:00:00Z'
    if date_finish == 'T00:00:00Z':
        date_finish = '2900-00-00T00:00:00Z'

    # Sign in
    sys.stdout.write(f"\n\n-Sign in GitHub-\n")
    sign_in = github_resp(url=url_git, login=mail_pass,
                          timeout=3, params=''
                          )
    stat_sign_in = sign_in[0]
    sys.stdout.write(f'\n{stat_sign_in}')

    # commits
    sys.stdout.write(f"\n-Get commits-\n")
    commits, comm_st = get_commits(url=url_commits, branch=branch,
                                   since=date_start, until=date_finish, timeout=3)
    if comm_st != 'Success!':
        return sys.stdout.write(f"{comm_st}\n")
    # Считаем коммиты авторов и сортируем по убыванию
    m_commit = Counter(commits).most_common(30)
    # Подготовка данных для построения таблицы
    row_commit = [['Name Author', 'Number commit']]
    [row_commit.append((str(cort[0]), str(cort[1]))) for cort in m_commit]
    # Построение таблицы
    sys.stdout.write(f'\nMost active author:\n')
    [sys.stdout.write(f'{line}\n') for line in pretty_table(row_commit, 2)]

    # pulls closed
    sys.stdout.write(f"\n-Get pulls closed-\n")
    closed_pulls, pulls_stat_cl = get(url_pulls, 'closed', branch, 3,
                                      start=date_start, finish=date_finish
                                      )
    if pulls_stat_cl != 'Success!':
        return sys.stdout.write(f"{pulls_stat_cl}\n")
    sys.stdout.write(f'\nExamples pulls closed:\n')
    numb_cl_pull = 5  # число выводимых примеров
    [sys.stdout.write(f'{pull[0]}\n') for index, pull in enumerate(closed_pulls)
     if index < numb_cl_pull]
    sys.stdout.write(f'\nNumber pulls closed = {len(closed_pulls)}\n')

    # pulls open
    sys.stdout.write(f"\n-Get pulls open-\n")
    open_pulls, pulls_stat_op = get(url_pulls, 'open', branch, 3,
                                    start=date_start, finish=date_finish
                                    )
    if pulls_stat_op != 'Success!':
        return sys.stdout.write(f"{pulls_stat_op}\n")
    sys.stdout.write(f'\nExamples pulls open:\n')
    numb_op_pull = 5  # число выводимых примеров
    [sys.stdout.write(f'{pull[0]}\n') for index, pull in enumerate(open_pulls)
     if index < numb_op_pull]
    sys.stdout.write(f'\nNumber pulls open = {len(open_pulls)}\n')

    sys.stdout.write(f'\nExamples old pulls:\n')
    age_pulls = valid_age(open_pulls, 30)
    numb_old_pull = 5  # число выводимых примеров
    [sys.stdout.write(f'{pull[0]}\n') for index, pull in enumerate(age_pulls)
     if index < numb_old_pull]
    sys.stdout.write(f'\nNumber old pulls = {len(age_pulls)}\n')

    # issue closed
    sys.stdout.write(f"\n-Get issue closed-\n")
    closed_issue, issue_stat_cl = get(url_issue, 'closed', branch, 3,
                                      start=date_start, finish=date_finish
                                      )
    if issue_stat_cl != 'Success!':
        return sys.stdout.write(f"{issue_stat_cl}\n")
    sys.stdout.write(f'\nExamples issue closed:\n')
    numb_cl_issue = 5  # число выводимых примеров
    [sys.stdout.write(f'{issue[0]}\n') for index, issue in enumerate(closed_issue)
     if index < numb_cl_issue]
    sys.stdout.write(f'\nNumber issue closed = {len(closed_issue)}\n')

    # issue open
    sys.stdout.write(f"\n-Get issue open-\n")
    open_issue, issue_stat_op = get(url_issue, 'open', branch, 3,
                                    start=date_start, finish=date_finish
                                    )
    if issue_stat_op != 'Success!':
        return sys.stdout.write(f"{issue_stat_op}\n")
    sys.stdout.write(f'\nExamples issue open:\n')
    numb_op_issue = 5  # число выводимых примеров
    [sys.stdout.write(f'{issue[0]}\n') for index, issue in enumerate(open_issue)
     if index < numb_op_issue]
    sys.stdout.write(f'\nNumber issue open = {len(open_issue)}\n')

    sys.stdout.write(f'\nExamples old issue:\n')
    age_issue = valid_age(open_issue, 14)
    numb_old_issue = 5  # число выводимых примеров
    [sys.stdout.write(f'{issue[0]}\n') for index, issue in enumerate(age_issue)
     if index < numb_old_issue]
    sys.stdout.write(f'\nNumber old issue = {len(age_issue)}\n')


if __name__ == '__main__':
    main()
