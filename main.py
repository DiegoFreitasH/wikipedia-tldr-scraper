#! /usr/bin/python3.8
import re
import requests
import argparse
from bs4 import BeautifulSoup
from requests.exceptions import RequestException

USE_RICH = True
try:
    from rich import print
    from rich.panel import Panel
except ImportError as e:
    USE_RICH = False

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def remove_reference_numbers(text: str) -> str:
    return re.sub(r'\[\d+\]', '', text)

def get_title(soup: BeautifulSoup) -> str:
    return soup.find('h1', {'id': 'firstHeading'}).text

def get_may_refer_to_list(soup: BeautifulSoup) -> str:
    list_items = soup.find('div', {'class': 'mw-parser-output'}).find_all('li', class_=None)
    return '\n'.join([item.text for item in list_items])

def get_summary(soup: BeautifulSoup) -> str:
    p_list = soup.find_all('p', limit=5)
    summary = 'Could not find summary'
    
    for p in p_list:
        if len(p.text) > 5:
            summary = p.text
            break
    summary = summary.strip()
    if summary.endswith('may refer to:'):
        summary += '\n' + get_may_refer_to_list(soup)
    

    return remove_reference_numbers(summary)

def render_summmay(title: str, link: str, summary_text: str) -> None:
    if USE_RICH:
        print(Panel(
            summary_text, 
            title=f'[bold magenta]{title}[/bold magenta]',
            subtitle=f'[italic cyan]{link}[/italic cyan]',
            padding=(1,1)
        ))
    else:
        print(f'Title: {bcolors.BOLD}{bcolors.HEADER}{title}{bcolors.ENDC}')
        print(f'Link: {bcolors.OKBLUE}{link}{bcolors.ENDC}', end='\n\n')
        print(summary_text)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scrape summary paragraph from wikipedia')
    parser.add_argument('search', nargs='+')

    args = parser.parse_args()
    
    prefix = 'https://en.wikipedia.org/wiki/'
    query = "_".join(args.search)
    
    processed_query = '_'.join(query.split())
    
    endpoint = f'{prefix}{processed_query}'
    req = requests.get(endpoint)

    if req.status_code != 200:
        raise RequestException(f'Failed to get: {endpoint}')

    soup = BeautifulSoup(req.text, 'html.parser')
    
    summary = get_summary(soup)
    title = get_title(soup)
    
    render_summmay(title, endpoint, summary)