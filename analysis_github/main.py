import collections

import requests
import random
from time import sleep
from collections import Counter

# ПАРАМЕТРЫ ВВОДИТЬ С ПАНЕЛИ
URL = 'https://api.github.com'
URL_REP = f'https://api.github.com/repos/geekcomputers/Python'
URL_COMMITS = f'{URL_REP}/commits'
NAME_PASS = ('sunday8361@gmail.com', 'cfb71627b6cfae6e5daf0c718b86f59c')
BRANCH = 'master'
DATA_START = '2018-03-28T14:33:18Z'  # если не задано, то '2000-00-00T00:00:00Z'
DATA_FINISH = ''  # если не задано, то ''


# '2016-01-28T14:33:18Z'


def respons(**kwargs):
    """Запрос к GitHub"""

    try:
        r = requests.get(url=kwargs['url'],
                         auth=kwargs['login'],
                         timeout=kwargs['timeout'],
                         params=kwargs['params']
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
        print(f"Success!\n")
        r.encoding = 'utf-8'
        return r.json()


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
    sign_in = respons(url=URL, login=NAME_PASS, timeout=3, params='')
    # print(sign_in)

    print(f"Get commits")
    sleep(random.randint(1, 4))
    all_commits = respons(url=URL_COMMITS, login='', timeout=3,
                          params={"sha": BRANCH,
                                  "since": DATA_START,
                                  "until": DATA_FINISH}
                          )
    print(all_commits)

    # Парсим авторов коммитов
    most_commit = []
    for i in range(0, 29, 1):
        try:
            most_commit.append(
                all_commits[i]['commit']['author']['name']
            )
        except IndexError:
            print(f'All names of the commit authors collected!\n\n')
            break
    # Считаем коммиты авторов
    a = Counter(most_commit).most_common(30)
    print(a)

    # Разделяем словарь на два списка
    # l1 = []
    # l2 = []
    # for key, val in a.items():
    #     l1.append(key)
    #     l2.append(val)
    # print(f'{l1}\n{l2}')

    # Подготовка данных для построения таблицы
    # author_name = [['Name Author', 'Number commit']]
    # for i in range(0, len(l1), 1):
    #     try:
    #         author_name.append((str(l1[i]), str(l2[i])))
    #     except IndexError:
    #         print(f'Index Error\n')
    #         break
    # # print(author_name)
    #
    # # Построение таблицы
    # print(f'Most active author')
    # for line in pretty_table(author_name, 2):
    #     print(line)

    # Подготовка данных для построения таблицы
    most_commit = [['Name Author', 'Number commit']]
    for cort in a:
        try:
            most_commit.append((str(cort[0]), str(cort[1])))
        except IndexError:
            print(f'Index Error\n')
            break
    print(most_commit)

    # Построение таблицы
    print(f'Most active author')
    for line in pretty_table(most_commit, 2):
        print(line)
