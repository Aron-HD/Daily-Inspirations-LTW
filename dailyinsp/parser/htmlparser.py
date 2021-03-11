from bs4 import BeautifulSoup as BS
import requests


class HtmlData:
    """docstring for HtmlData"""

    def __init__(self, html):
        self.html = html
        self.data = {}

    def process_text(self):
        """Extract the data from converted html."""

        soup = BS(self.html, 'html.parser')
        paras = soup.find_all('p')
        # append first three paragraphs
        self.data.update({
            "insp_day": paras[0].text,
            "insp_title": paras[1].text,
            "insp_intro": paras[2].text,
            "articles": [],
        })

        article = {}
        for p in paras[3:]:
            if p.find('a', href=True):
                if 'lovethework' in p.a['href']:
                    article["article_link"] = p.a['href']
            elif p.find('strong') and not p.text.endswith('.'):
                article["article_title"] = p.text.split(' / ')[1]
            else:
                article["article_desc"] = p.text

            keys = ('article_title', 'article_desc', 'article_link')
            # append article object to articles list and reset once all keys are filled
            if all(k in article.keys() for k in keys):
                self.data['articles'].append(article)
                # log.info(article)
                article = {}

    def process_ids(self):
        """Get ids from each article link in collection."""

        for art in self.data["articles"]:
            if art["article_link"]:
                link = art["article_link"]
                # extract campaign and asset ids from link if present
                if "?asset=" in link:
                    ids = link.split("?asset=")
                    campaign = ids[0]
                    asset = ids[1].replace("&play=1", "")
                else:
                    campaign = link
                    asset = False

                # maybe better to split on '-' and get [-1]
                art["campaign_id"] = campaign.split('-')[-1]  # [-6::]
                art["asset_id"] = asset

                # replace with real title using the non asset link
                # art["article_title"] = HtmlData.request_title(campaign)
        return self.data

    @staticmethod
    def request_title(url):
        """Gets the title from the actual link page."""
        r = requests.get(url)
        soup = BS(r.text, 'html.parser')
        titles = soup.find_all('h1', {"class": "*title"})
        print(titles)
        correct_title = None
        return correct_title


if __name__ == "__main__":
    from htmldata import data as testdata
    html_data = HtmlData(testdata)
    html_data.process_text()
    [print(i) for i in html_data.process_ids()]
