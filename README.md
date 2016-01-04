# style_scraper
Webscraper for the Best of Style Weekly from 2011-2013

This is *not* real-world ready. You'll need to set up a MySql database first - then update scrape_style.py with your credentials and run! Will definitely break if they've reformatted their site at all since I wrote this.

((If I were writing this now, I'd swap out MySQL for sqlite, use SQLAlchemy instead of hardcoded SQL text, and swap out all the PHP for Flask/Django, but here we are))
