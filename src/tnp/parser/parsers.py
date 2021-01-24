import os
import json
import pickle
import requests
from bs4 import BeautifulSoup as BS
from abc import ABC, abstractmethod
from datetime import datetime as dt
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from tnp.parser import HOST, PREVIEW_URL, BASE_DIR

class _Base(type):
    def __init__(cls, name, bases, attr_dict):
        super().__init__(name, bases, attr_dict)

    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        if cls.__name__ == "Preview":
            cls.__bases__[0].page = obj._Preview__num_page
        return obj

class BaseMeta(metaclass=_Base):
    """Base Meta class""" 

class BaseParser(BaseMeta):
    def _get_page(self, url):
        if hasattr(self, "page"):
            min_date = dt.strptime("03.10.2000", "%d.%m.%Y")
            page_date = dt.strptime(self.page, "%d.%m.%Y")
            max_date = dt.now()
            #max_date = f"{dt.now():%d.%m.%Y}"
            print(self.page)
            if page_date < min_date: 
                raise ValueError("Page is < 03.10.2000")
            if page_date > max_date:
                raise ValueError("Page is > today")
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

    def __iter__(self):
        self.__cursor = 0
        return self

    def __next__(self):
        if self.__cursor == len(self.__links):
            raise StopIteration
        try:
            return self.__links[self.__cursor]
        finally:
            self.__cursor +=1

    def __getitem__(self, index):
        try:
            if isinstance(index, int):
                demand = self.__links[index]
                return demand
            elif isinstance(index, slice):
                obj = Preview()
                self._Preview__links = self.__links[index]
                return obj
            else:
                raise TypeError
        except TypeError:
            print("List indices must be integer or slices")
        
    def save_to_file(self, name):
        path = os.path.join(BASE_DIR, name + ".bin")
        pickle.dump(self.__links, open(path, "wb"))

    def save_to_json(self, name):
        path = os.path.join(BASE_DIR, name + ".json")
        json.dump(self.__links, open(path, "w"))

class NewsParser(BaseParser):
    def __init__(self, url):
        self._url = url
        self.news = {}
    
    def get_news(self):
        try:
            html = self._get_page(self._url)
        except ValueError as error:
            print(error)
        else:
            box = html.find("div", attrs={"class": "b-article"})
            if box is not None:
                self.news["head"] = box.find("h1").text
                box_date = box.find("time", attrs={"itemprop": "datePublished"})
                if box_date is not None:
                    self.news["date"] = dt.fromisoformat(box.date.get("dt")).timestamp()
                list_img = box.find_all("img")
                self.news["scr_img"] = []
                if list_img is not None:
                    for img in list_img:
                        self.news["src_img"].append(img.attrs["src"])
                if box.find("div", attrs={"id": "article_body"}) is not None:
                    text_block = box.find("div", attrs={"id": "article_body"}).text
                    self.news["text"] = text_block
                  


if __name__ == "__main__":
    parser = Preview(page="23.01.2021")
    parser.get_links()
    print(parser._Preview__links.__len__())
    #print(parser[1])
    print(parser[1:4])
    #print(parser["key"])
    # parser.save_to_json("tmp_links_08.01.2021")
    # parser.save_to_file("tmp_links_08.01.2021")