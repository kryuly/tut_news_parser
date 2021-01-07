import os
import json
import pickle
import requests
from bs4 import BeautifulSoup as BS
from abc import ABC, abstractmethod
from datetime import datetime as dt

from tnp.parser import DEFAULT_USER_AGENT, HOST, PREVIEW_URL, BASE_DIR


class BaseParser(ABC):
    def _get_page(self, url):
        response = requests.get(url)
        if response.status_code == 200:
            return BS(response.text, features="html.parser")
        raise ValueError("Response not 200")

    @abstractmethod
    def save_to_file(self, name: str) -> None:
        """Save news to file
        Args:
            name (str): file name
        """        

    @abstractmethod
    def save_to_json(self, name: str) -> None:
        """Save news to json file
        Args:
            name (str): file name
        """        


class Preview(BaseParser):
    def __init__(self, **kwargs):
        n = dt.now()
        n_now = n.strftime("%d.%m.%Y")
        self.__num_page = kwargs.get("page") or n_now
        self.__links = []

    def get_links(self):
        try:
            html = self._get_page(PREVIEW_URL.format(HOST, self.__num_page))
        except ValueError:
            self.__links = []
        else:
            top_box = html.find("div", attrs={"class": "news-top"})
            box = html.find_all("div", attrs={"class": "b-news"})
            box.append(top_box)
            if box is not None:
                for section in box:
                    sections = section.find_all("div", attrs={"class": "news-entry"})
                    if sections is not None:
                        for a in sections:
                            #link = a.find("a", attrs={"class": "entry__link"})
                            link = a.find("a")
                            print(link.get("href"), end="\n\n")
                            self.__links.append(link.get("href"))
            else:
                self.__links = []

    def save_to_file(self, name):
        path = os.path.join(BASE_DIR, name + ".bin")
        pickle.dump(self.__links, open(path, "wb"))

    def save_to_json(self, name):
        path = os.path.join(BASE_DIR, name + ".json")
        json.dump(self.__links, open(path, "w"))


if __name__ == "__main__":
    parser = Preview(page="07.01.2021")
    parser.get_links()
    print(parser._Preview__links.__len__())
    parser.save_to_json("links_07.01.2021")
    parser.save_to_file("links_07.01.2021")