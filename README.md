# Twitter Scraper (Python + Selenium)

A simple Python project that scrapes Twitter content using **Selenium** with the Chrome engine.  
It uses selenium instead of simpler scrapers because they often get flagged by Twitter’s bot detection, this project simulates real browser behavior scrolling, clicking, and interacting with HTML elements

---

## Features

- **Robust scraping with Selenium + ChromeDriver**
  - Uses a full browser engine to bypass Twitter’s bot detection.
  - Manually controls the browser: scroll bars, clicks, and navigation.

- **Flexible input**
  - Enter your Twitter credentials and a target link:
    - A specific post to scrape comments
    - A user account
    - A search term
    - Your own likes, bookmarks, or private groups (which the official API cannot access).

- **Rich tweet data collection**
  - Saves:
    - Tweet text
    - Username of poster
    - Date posted
    - Number of likes
    - Number of comments
    - Media attachments (images, GIFs, videos)

- **Smart navigation**
  - Detects loading elements (like the spinning circle) to know when to stop scrolling.
  - Confirms successful login before scraping begins.

---

## 🛠️ Tech Stack

- **Python 3.x**
- **Selenium WebDriver**
- **ChromeDriver**
- **SQL** for storing scapped data
