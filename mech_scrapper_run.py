import mechanicalsoup
import nltk
from sklearn.feature_extraction.text import CountVectorizer
import json
import time
import pickle

SITE = "http://fanfiction.net"

class Scrapper:
    def __init__(self,site):
        self.site = site
        self.__browser = mechanicalsoup.StatefulBrowser(raise_on_404 = True)
        self.response = self.__browser.open(self.site)
        self.links = []
        self.chapters = []
        self.downloaded = []
        with open("dict.txt","a+") as f:
            f.close()
    def open(self,site):
        return self.__browser.open(site)
    def follow_link(self,follow_link):
        self.__browser.follow_link(follow_link)
        return (self.__browser.get_url())
    def filtered_fan_fiction(self):
        URL = self.__browser.get_url()
        Filters = ('srt', 'lan', 'len', 'p') # list of desired filters
        FilterValues = (3, 1, 0, 2) # list of values for filters
        FilterSet = ''
        for i in range(len(Filters)):
            FilterSet += '&%s=%d' % (Filters[i], FilterValues[i])

        newURL = str(URL) + '?' + FilterSet
        return newURL
    @staticmethod
    def cleaning(soup): #fuction to cleaning html leftovers from soup.get_text
        splitted = soup.split('\n')
        result = splitted
        d = 0
        for n in range(len(splitted)):
            if splitted[n] == '});':
                p = n
                break
        for n in range(len(splitted)):
            if splitted[n] == '    function review_init() {':
                d = n
                result = splitted[p+3:d-2]
                break
        result = [frag.replace("\'",'') for frag in result]
        result = [frag.replace("\r",'') for frag in result]
        return result

    def preparing_links(self):
        l1 = self.__browser.links()
        l2 = []
        self.links = []
        l4 = []
        l5 = []
        self.chapters = []

        for n in range(len(l1)):
            if 'stitle' in str(l1[n]):
                l2.append(l1[n])
                l4.append(l1[n+1])

        for n in l2:
            beglink = str(n).find('href="')
            endlink = str(n).find('"><')
            a = str(n)[beglink+6:endlink]
            self.links.append(a)

        for n in l4:
            beglink = str(n).find('href="')
            endlink = str(n).find('"><')
            a = str(n)[beglink+6:endlink]
            l5.append(a)

        for n in l5:
            a = n.split('/')
            self.chapters.append(a[3])


        return self.links,self.chapters, #list of links to download each fanfic; list of chapters of each fanfic piece
    def download_list(self,ran_giv = 2,pr_link=True,save_file=True): #links and chapters are product of preparing_links function;
        #ran_giv is a number of links that are going to be downloaded; for all links  use len(links);
        #pr_link is a decision whether print links during downloading or not.
        self.__ran_giv = ran_giv
        links = self.checkfiles()
        chapters = self.chapters
        downloaded = self.downloaded
        data_sample = []
        story_name = []

        for n in range(ran_giv):
            old_one = links[n].split('/')

            for r in range(int(chapters[n])):
                one_fan_fic = []
                new_one = ''
                old_one[3] = str(r)
                new_one += self.site

                for n in range(len(old_one)-1):
                    new_one += old_one[n]
                    new_one += '/'
                new_one += old_one[-1]

                downloaded.append(new_one)
                if pr_link == True:
                    print(new_one)

                self.__browser.open(new_one)
                __soup = self.__browser.get_current_page()
                page = __soup.get_text()
                self.__cleaned = self.cleaning(page)
                one_fan_fic.append(self.__cleaned)
            data_sample.append(one_fan_fic)

            for i in range(len(downloaded)):
                for i in range(len(links)):
                    _temp = links[i]
                    _temp = links[i].split("/")[-1]
                    story_name.append(_temp)


        with open ('dict.txt','a') as h:
            for i in downloaded:
                h.write(i + "\n")
            h.close()
        print ("Operation completed!")
        if save_file:
            for i in range(len(data_sample)):
                with open (str(story_name[i]) + '.txt','a') as k:
                    k.write(str(one_fan_fic))
                    k.close()
        return set(story_name)
    def checkfiles(self):
        __links = self.links
        print ("Links avalible to scrap:", len(self.links))
        with open ('dict.txt','r') as g:
            histor = g.read()
            for j in range(len(__links)):
                for i in __links:
                    if i in histor:
                        __links.remove(i)
                    else:
                        pass
            g.close()
        print ("Links not downloaded:", len(__links))
        print ('You selected {} links to download.'.format(self.__ran_giv))
        return __links


if __name__ == '__main__':
    from mech_scrapper import *
    scrap = Scrapper(SITE)
    scrap.follow_link('movie')
    scrap.follow_link('Star-Wars')
    scrap.filtered_fan_fiction()
    scrap.open(scrap.filtered_fan_fiction())
    scrap.preparing_links()
    print ("Scrapper will now download the fanfiction into files. \n")
    answer = input("Do you want to continue? [Y/N] \n")
    if answer.upper() == "Y":
        x = input('How many? \n ')
        if x.upper() is "ALL":
            story = scrap.download_list(ran_giv=len(scrap.links))
        else :
            story = scrap.download_list(ran_giv=int(x))
