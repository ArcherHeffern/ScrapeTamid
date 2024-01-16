from bs4 import BeautifulSoup
import argparse
from dataclasses import dataclass
from typing import Optional
import requests
import time
from scrapers.scrapeConsulting import get_consulting_content
from scrapers.scrapeTech import get_tech_content

payload = {
    'Email': None,
    'password': None,
    'submit': 'Sign in',
    '__EVENTTARGET': '',
    '__EVENTARGUMENT': ''
}


@dataclass
class Config:
    start: int
    end: int
    email: str
    password: str
    category: str
    out: str
    delay: float
    debug: bool = False
    test: Optional[int] = None
    base_url: str = 'https://apps.tamidgroup.org/Consulting/Company/posting?id='
    login_url = 'https://apps.tamidgroup.org/login'


def main():
    config = parse_args()
    try:
        if config.category == 'tech':
            scraper(config, get_tech_content)
        else:
            scraper(config, get_consulting_content)
    except KeyboardInterrupt:
        print("\nExiting")


def parse_args() -> Config:
    parser = argparse.ArgumentParser(
        prog='tamid scraper',
        description='A webscraper to view all of tamids groups projects as one of their PMs in an easily digestable html file',
        epilog="""
            It is up to you to figure out what range to scan. I would suggest looking at the url of the projects offered and make an estimate. A range of 2000 is sufficient. The output file is in html format
        """)
    parser.add_argument('-c', '--category',
                        choices=['tech', 'consulting'], default='tech', help='Choose track to scrape')
    parser.add_argument('out', help='Output file name')
    parser.add_argument('email', help='Tamid Platform email')
    parser.add_argument('password', help='Tamid Platform password')
    parser.add_argument(
        'start', type=int, help='Starting index')
    parser.add_argument('end', type=int, help='Ending index (inclusive)')
    parser.add_argument('-d', '--delay', type=int, default=.5,
                        help='Delay to prevent being ratelimited')
    args = parser.parse_args()

    config = Config(
        start=args.start,
        end=args.end,
        email=args.email,
        password=args.password,
        category=args.category,
        out=args.out,
        delay=args.delay
    )
    payload['Email'] = config.email
    payload['password'] = config.password
    return config


def scraper(config: Config, scraper_function):

    valid_count = 0

    with requests.Session() as s:
        start_time = time.time()
        if not login(config.login_url, payload, s):
            print('authetication error')
            exit(1)
        print("Logged in")
        with open(config.out, 'w') as f:

            f.write("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Projects</title>
</head>
<body>""")

            for i in range(config.start, config.end + 1):
                print(f"{i - config.start + 1}/{config.end - config.start + 1}", end="")
                internal_start = time.time()
                html = s.get(config.base_url + str(i))
                html = html.text
                company = scraper_function(i, html, config.base_url)
                if company:
                    print_to_output_file(company, f)
                    valid_count += 1
                internal_end = time.time()
                time.sleep(max(0, config.delay - (internal_end - internal_start)))

                # Stats
                f.write("</body></html>")
                if config.debug:
                    total_time = time.time() - start_time
                    print(
                        f"Complete\nRuntime: {total_time}\nRuntime minus delay: {total_time - config.delay * (config.end - config.start)}\nValid items: {valid_count}")


def login(url, payload, session):
    """Returns boolean if logging in was successful"""
    page = session.get(url)
    soup = BeautifulSoup(page.content, 'lxml')
    viewStateElement = soup.select_one("#__VIEWSTATE")
    viewStateGeneratorElement = soup.select_one("#__VIEWSTATEGENERATOR")
    eventValidationElement = soup.select_one("#__EVENTVALIDATION")
    if not viewStateElement or not viewStateGeneratorElement or not eventValidationElement:
        raise Exception("Could not find __VIEWSTATE, __VIEWSTATEGENERATOR, or __EVENTVALIDATION \
                      This could imply the login page has changed")
    payload["__VIEWSTATE"] = viewStateElement["value"]
    payload["__VIEWSTATEGENERATOR"] = viewStateGeneratorElement["value"]
    payload["__EVENTVALIDATION"] = eventValidationElement["value"]

    session.post(url, data=payload)

    open_page = session.get(
        "https://apps.tamidgroup.org/Consulting/PMPD/ConsultingDashboard")

    # kinda hacky but it works
    return not page.text[:1000] == open_page.text[:1000]


def print_to_output_file(content: dict, f):
    """Takes dict as input and writes the content to output file"""
    for key, value in content.items():
        if key == "url" or key == "website":
            f.write(f"<div><b>{key}</b>: <a href={value}>{value}</a><br><br>")
        else:
            f.write(f"<div><b>{key}</b>: {value}</div><br>")
    f.write("<hr><br>")


if __name__ == '__main__':
    main()
