import csv
import io
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common import exceptions
import chromedriver_autoinstaller

def scrape(url):
    """
    Extracts the comments from the Youtube video given by the URL.

    Args:
        url (str): The URL to the Youtube video

    Raises:
        selenium.common.exceptions.NoSuchElementException:
        When certain elements to look for cannot be found
    """

    # Automatically download and install the correct version of chromedriver
    chromedriver_autoinstaller.install()

    # Initialize the Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

    # Navigates to the URL and suspends execution for (at least) 5 seconds (this gives time for the page to load).
    driver.get(url)
    time.sleep(5)

    try:
        # Extract the elements storing the video title and comment section.
        title = driver.find_element(By.XPATH, '//*[@id="container"]/h1/yt-formatted-string').text
        comment_section = driver.find_element(By.XPATH, '//*[@id="comments"]')
    except exceptions.NoSuchElementException:
        # Note: Youtube may have changed their HTML layouts for videos, so raise an error for sanity sake in case the elements provided cannot be found anymore.
        error = "Error: Double check selector OR element may not yet be on the screen at the time of the find operation"
        print(error)
        driver.close()
        return

    # Scroll into view the comment section, then allow some time for everything to be loaded as necessary.
    driver.execute_script("arguments[0].scrollIntoView();", comment_section)
    time.sleep(7)

    # Scroll all the way down to the bottom in order to get all the elements loaded (since Youtube dynamically loads them).
    last_height = driver.execute_script("return document.documentElement.scrollHeight")

    while True:
        # Scroll down 'til "next load".
        driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

        # Wait to load everything thus far.
        time.sleep(2)

        # Calculate new scroll height and compare with last scroll height.
        new_height = driver.execute_script("return document.documentElement.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # One last scroll just in case.
    driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")

    try:
        # Extract the elements storing the usernames and comments.
        username_elems = driver.find_elements(By.XPATH, '//*[@id="author-text"]')
        comment_elems = driver.find_elements(By.XPATH, '//*[@id="content-text"]')
    except exceptions.NoSuchElementException:
        error = "Error: Double check selector OR element may not yet be on the screen at the time of the find operation"
        print(error)
        driver.close()
        return

    print("> VIDEO TITLE: " + title + "\n")

    with io.open('results.csv', 'w', newline='', encoding="utf-16") as file:
        writer = csv.writer(file, delimiter=",", quoting=csv.QUOTE_ALL)
        writer.writerow(["Username", "Comment"])
        for username, comment in zip(username_elems, comment_elems):
            writer.writerow([username.text, comment.text])

    driver.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Error: Please provide a YouTube video URL as an argument.")
        print("Usage: python main.py YOUTUBE_VIDEO_URL")
    else:
        scrape(sys.argv[1])
