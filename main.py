import os
import requests
from argparse import ArgumentParser
from urllib.parse import urlparse
from dotenv import load_dotenv


def create_parser():
    parser = ArgumentParser(description='Преобразует сайт в короткую ссылку или выводит'
                                        ' кол-во переходов по короткой ссылке')
    parser.add_argument('site', type=str, help='адрес сайта или короткая ссылка')
    return parser


def is_bitlink(token, site):
    parsed_link = urlparse(site)
    bitlink = f'{parsed_link.netloc}{parsed_link.path}'
    url = f'https://api-ssl.bitly.com/v4/bitlinks/{bitlink}'
    headers = {'Authorization': f'Bearer0 {token}'}
    response = requests.get(url, headers=headers)
    return response.ok


def shorten_link(token, site):
    url = f'https://api-ssl.bitly.com/v4/bitlinks'
    data = {'long_url': site}
    headers = {'Authorization': f'Bearer {token}'}
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    api_answer = response.json()
    return api_answer.get('link')


def count_clicks(token, bitlink):
    headers = {'Authorization': f'Bearer {token}'}
    parsed_link = urlparse(bitlink)
    bitlink = f'{parsed_link.netloc}{parsed_link.path}'
    url = f'https://api-ssl.bitly.com/v4/bitlinks/{bitlink}/clicks/summary'
    payload = {
        'unit': 'day',
        'units': "-1"
    }
    response = requests.get(url, headers=headers, params=payload)
    response.raise_for_status()
    api_answer = response.json()
    return api_answer.get('total_clicks')


def main():
    load_dotenv()
    try:
        parser = create_parser()
        arguments = parser.parse_args()
        site = arguments.site.strip()
        api_key = os.environ.get('BITLY_TOKEN')

        if is_bitlink(api_key, site):
            total_clicks = count_clicks(api_key, site)
            print(f'По вашей ссылке перешли {total_clicks} раз(а)')

        else:
            bitlink = shorten_link(api_key, site)
            print('Битлинк', bitlink)

    except (requests.exceptions.HTTPError, requests.exceptions.InvalidSchema, requests.exceptions.ConnectionError) as e:
        error_data = e.response
        error_code = error_data.status_code
        if error_code == 400:
            print('Вы ошиблись при вводе сайта')
        elif error_code == 403:
            print('Доступ запрещён. Проверьте токен')
        else:
            print('Ошибка доступа: ', error_code)

    except FileNotFoundError:
        print('Вы ошиблись в имени скрипта main.py или пути к нему')


if __name__ == '__main__':
    main()
