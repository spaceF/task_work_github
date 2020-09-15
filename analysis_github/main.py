import requests
import random
from time import sleep


# ПАРАМЕТРЫ ВВОДИТЬ С ПАНЕЛИ
URL = 'https://api.github.com'
URL_REP = f'https://api.github.com/repos/IgnorantGuru/spacefm'
URL_COMMITS = f'{URL_REP}/commits'
NAMEPASS = ('sunday8361@gmail.com', 'cfb71627b6cfae6e5daf0c718b86f59c')
BRANCH = 'alpha'
DATA_START = '2018-03-28T14:33:18Z' # если не задано, то '2000-00-00T00:00:00Z'
DATA_FINISH = '' # если не задано, то ''

# '2016-01-28T14:33:18Z'


def test(**kwargs):

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


if __name__ == '__main__':
    print(f"Sign in GitHub")
    sleep(random.randint(1, 4))
    signin = test(url=URL, login=NAMEPASS, timeout=3, params='')
    # print(signin)

    # Получаем репозиторий для анализа
    print(f"Get repos")
    sleep(random.randint(1, 4))
    all_rep = test(url=URL_REP, login='', timeout=3,
                   params={"since": DATA_START,
                           "until": DATA_FINISH})
    # print(f"{all_rep}")
    print(f"Name repository: {all_rep['name']}\n"
          f"Default branch: {all_rep['default_branch']}\n")

    # Получаем коммиты репозитория
    print(f"Get commits")
    sleep(random.randint(1, 4))
    all_commits = test(url=URL_COMMITS, login='', timeout=3,
                       params={"sha": BRANCH,
                               "since": DATA_START,
                               "until": DATA_FINISH}
                       )
    # print(all_commits)


    for i in range(0, 29 ,1):
        # commit = all_commits[0]['commit']
        author_name = all_commits[0]['commit']['author']['name']

    print(commit)
    print(author_name)

    #print(author_)

    #for i in range(0, 29, 1):
      #  try:
        #    c = all_commits[i]['commit']
       # except IndexError as erri:
        #    print(f'Index Error: {erri}')
        #    break
       # else:
         #   print(c)

