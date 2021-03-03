import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import InvalidArgumentException
from selenium.webdriver.support import expected_conditions as EC
# import login details from secret credentials file
from .driver import credentials

chrome_options = Options()
chrome_options.add_argument(
    r"user-data-dir=C:\Users\arondavidson\AppData\Local\Google\Chrome\User Data\Profile 1")
# chrome_options.add_argument('--headless')
# chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])


class GemBot:
    def __init__(self, data, open_access, guest_edited):
        self.bot = webdriver.Chrome(
            options=chrome_options,
            # switch to driver/chromedriver.exe with sys path append
            executable_path=r"C:\Users\arondavidson\AppData\Local\Programs\Python\Python37\chromedriver.exe"
        )
        self.data = data
        self.open_access = open_access
        self.guest_edited = guest_edited
        self.url = 'https://gemini-backend.lovethework.com/cms/inspirations/new'
        self.usr = credentials.login['EMAIL_ADDRESS']
        self.pwd = credentials.login['PASSWORD']

    def login(self):
        bot = self.bot
        bot.implicitly_wait(10)
        bot.get(self.url)
        username = WebDriverWait(bot, 10).until(
            EC.visibility_of_element_located((By.ID, 'okta-signin-username'))
        )
        password = WebDriverWait(bot, 10).until(
            EC.visibility_of_element_located((By.ID, 'okta-signin-password'))
        )
        username.clear()
        username.send_keys(self.usr)
        password.clear()
        password.send_keys(self.pwd)
        WebDriverWait(bot, 5).until(EC.visibility_of_element_located(
            (By.CSS_SELECTOR, 'div[aria-live="polite"]')))
        bot.find_element(By.ID, "okta-signin-submit").click()
        time.sleep(10)  # have to enter okta TFA

    def inspiration_details(self):
        """Inputs data dictionary extracted from text file into initial form for the New Inspiration."""
        bot = self.bot
        # find elements

        # Title and Introduction
        title = WebDriverWait(bot, 15).until(
            EC.visibility_of_element_located((By.ID, 'inspiration_title'))
        )
        intro = WebDriverWait(bot, 15).until(
            EC.visibility_of_element_located(
                (By.ID, 'inspiration_introduction'))
        )
        # Live at date options
        day = Select(bot.find_element(
            By.CSS_SELECTOR, '#inspiration_live_at_day'))
        month = Select(bot.find_element(
            By.CSS_SELECTOR, '#inspiration_live_at_month'))
        year = Select(bot.find_element(
            By.CSS_SELECTOR, '#inspiration_live_at_year'))
        time.sleep(1)
        # Show on site tickbox
        bot.find_element(By.ID, 'inspiration_visible').click()
        time.sleep(1)
        # Guest editor tickbox
        if self.guest_edited:
            bot.find_element(By.ID, 'inspiration_guest_edit').click()
            time.sleep(1)

        # send / select data
        title.send_keys(self.data['insp_title'])
        intro.send_keys(self.data['insp_intro'])
        y = str(self.data['live_year'])
        m = str(self.data['live_month'])
        d = str(self.data['live_day'])
        # only select if year doesn't match
        if year.first_selected_option.text != y:
            year.select_by_visible_text(y)
        month.select_by_value(m)
        day.select_by_value(d)
        # Choose inspiration image file upload button
        try:
            bot.find_element(By.ID, 'inspiration_image').send_keys(
                self.data['img_path']
            )

            # save details if y
            if input('hit "y" for save, any key to cancel:') == 'y':
                save = bot.find_element(
                    By.CSS_SELECTOR, 'button[type="submit"]').click()
        except InvalidArgumentException as e:
            print(e)
            print(
                'error while finding image and saving...\nexiting without saving inspiration...'
            )

    def campaign_details(self):
        """Inputs data into subsequent form for each article object within the collection."""
        bot = self.bot
        time.sleep(3)
        for article in self.data['articles']:
            campaign_id = bot.find_element(
                By.ID, 'inspiration_campaign_campaign_id')
            campaign_id.clear()
            time.sleep(1)
            campaign_id.send_keys(article['campaign_id'])
            time.sleep(1)

            if article['asset_id']:
                asset_id = bot.find_element(
                    By.ID, 'inspiration_campaign_asset_id')
                asset_id.clear()
                time.sleep(1)
                asset_id.send_keys(article['asset_id'])
                time.sleep(1)
            name = bot.find_element(By.ID, 'inspiration_campaign_title')
            name.clear()
            time.sleep(1)
            name.send_keys(article['article_title'])
            time.sleep(1)
            desc = bot.find_element(By.ID, 'inspiration_campaign_description')
            desc.clear()
            time.sleep(1)
            desc.send_keys(article['article_desc'])
            time.sleep(2)

            # click open access
            if self.open_access:
                bot.find_element(
                    By.ID, 'inspiration_campaign_open_access').click()
                time.sleep(1)
            # return a list of open access links
            # article_link mixed with campaign id and inspiration number (198 etc.)
            if input('hit "y" for save, any key to cancel:') == 'y':
                save = bot.find_element(
                    By.CSS_SELECTOR, 'button[type="submit"]').click()

    def get_url(self):
        """Returns the resolved url of the new inspiration for sharing."""
        link = self.bot.current_url
        slug = link.split('/')[-1]
        # log.info('inspiration code:', slug)
        base = 'https://www.lovethework.com/inspiration/'
        url = base + slug
        # log.info('resolved url:', url)
        with requests.Session() as s:
            res = requests.get(url)
        return res.url
