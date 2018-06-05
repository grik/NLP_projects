import mechanicalsoup
import time
import json
# import nltk
# import pickle
from timeit import default_timer as timer
import re
from unidecode import unidecode
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
import re
from nltk.corpus import stopwords
import numpy as np
import os



SITE = "http://fanfiction.net"  # Default site to work on, tested.


class Scrapper:
    def __init__(self, site):
        self.site = site
        self.__browser = mechanicalsoup.StatefulBrowser(raise_on_404=True)
        self.response = self.__browser.open(self.site)
        self.linksOnPage = []
        self.linksToDownload = []

        with open("dict.txt", "a+") as f:  # file with history of downloads
            # f.close()
            pass

    def open(self, site):
        return self.__browser.open(site)

    def follow_link(self, follow_link):
        self.__browser.follow_link(follow_link)
        return (self.__browser.get_url())

    def filtered_fan_fiction(self):
        URL = self.__browser.get_url()
        Filters = ('srt', 'lan', 'len', 'p')  # list of desired filters
        FilterValues = (3, 1, 0, 2)  # list of values for filters
        FilterSet = ''
        for i in range(len(Filters)):
            FilterSet += '&%s=%d' % (Filters[i], FilterValues[i])

        newURL = str(URL) + '?' + FilterSet
        return newURL

    @staticmethod
    def cleaning(soup):
        '''Function to cleaning html leftovers from soup.get_text '''
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
        result = [frag.replace("\'", '') for frag in result]
        result = [frag.replace("\r", '') for frag in result]
        result = ''.join(result)
        return result
        return soup


    def preparing_links(self):
        l1 = self.__browser.links()
        l2 = []
        l4 = []
        l5 = []

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
        return self.links, self.chapters  # list of links to download each fanfic; list of chapters of each fanfic piece
    
    def preparing_links2(self):
        """This module is tasked with finding all links to stories on a search page of fanfiction.net. It takes a ResultSet of URLs, extracted from StatefulBrowser, and runs a regular expression.
        
        To reduce calcultions, the module searches only for links to the last chapters of stories. Then it reconstructs links to the firsts. Yeah, it's faster that way."""

        all_links = self.__browser.links()
        all_links = all_links[1::2]
        self.linksOnPage = re.findall(r'/s/[0-9]+/[0-9]+/[-a-zA-Z0-9]+', str(all_links))

        return self.linksOnPage

    def download_list(self,ran_giv=2,pr_link=True,save_file=True): #links and chapters are product of preparing_links function;
        #ran_giv is a number of links that are going to be downloaded; for all links  use len(links);
        #pr_link is a decision whether print links during downloading or not.
        # self.__ran_giv = ran_giv
        links = self.linksToDownload
        data_sample = []

        for n in range(0,ran_giv):
            split = links[n].split('/')
            story_number = split[2]
            chapters = split[3]
            story_name = split[4]
            one_fan_fic = []
            for r in range(1, int(chapters)+1):
                download_link = self.site + '/s/' + story_number + '/{}/'.format(r) + story_name
                if pr_link:
                    print(download_link)
                # Using mechanicalsoup to get and clean a page.
                self.__browser.open(download_link)
                __soup = self.__browser.get_current_page()
                page = __soup.get_text()
                page = unidecode(page) # THE SAVIOR OF MY SANITY
                self.__cleaned = self.cleaning(page)
                one_fan_fic.append(self.__cleaned)
            one_fan_fic = ''.join(one_fan_fic)

            data_sample.append(one_fan_fic)
            if save_file:
                with open (str(story_name) + '.txt','a') as k:
                        k.write(str(one_fan_fic))
                        # k.close()
                download_link = self.site + '/s/' + story_number + '/1/' + story_name
                with open ('dict.txt','a') as h:
                        h.write(download_link + "\n")
                        # h.close()       
        print ("Operation completed!")
        return data_sample # or set(story_name) depend on our needs.

    def checkfiles(self):
        __links = self.linksOnPage
        #print ("Links avalible to scrap:", len(self.links))
        with open ('dict.txt','r') as g:
            history = g.read()
            # g.close()
            for j in range(len(self.linksOnPage)):
                for i in __links:
                    split = i.split('/')
                    story_number = split[2]
                    if story_number in history:
                        __links.remove(i)
                        # print('bingo!') # for debug purposes
                    else:
                        pass
        self.linksToDownload = __links
        #print ("Links not downloaded:", len(__links))
        #print ('You selected {} links to download.'.format(self.__ran_giv))
        return self.linksToDownload
    
    @staticmethod
    def preparing_stories(stories_list):
        result_list = []
        for n in stories_list:
            result = re.sub("[^a-zA-Z]"," ",n)
            result = result.lower()
            result = result.split(' ')
            result = [w for w in result if w not in stopwords.words()]
            result = ' '.join(result)
            result_list.append(result)
        return result_list

    @staticmethod
    def array_words(stories_list):
        count = CountVectorizer(analyzer='word',tokenizer=None,
                          preprocessor = None,max_features = 5000)
        stories = preparing_stories(stories_list)
        transformed = count.fit_transform(stories)
        feature_array = transformed.toarray()
        return feature_array
    
    @staticmethod
    def read_stories_HDD():
        osdir = [os.listdir()[n] for n in range(len(os.listdir())) if 'txt' in os.listdir()[n]]
        osdir.remove('dict.txt')
        stories_list = []
        for n in osdir:
            chunk = open(n,'r').read()
            stories_list.append(chunk)
        return stories_list


if __name__ == '__main__':
    
    from mech_scrapper_run import *
    CATEGORY = 'movie'
    UNIVERSE = 'Star-Wars'
    scrap = Scrapper(SITE)
    print('Scrapper object created!')
    scrap.follow_link(CATEGORY)
    print('Processing to: ', CATEGORY)
    scrap.follow_link(UNIVERSE)
    print('Processing to: ', UNIVERSE)
    scrap.open(scrap.filtered_fan_fiction())
    
    # start = timer()
    # scrap.preparing_links()
    # end = timer()
    # print(end - start)

    # start = timer()
    scrap.preparing_links2()
    # end = timer()
    # print(end - start)
    
    print("Filtering and preparing links: ", 'DONE')
    print("Scrapper will now download the fanfiction into files. \n")
    print('=======================================================')
    print("Status:")
    print("Links on website:", len(scrap.linksOnPage))
    print("Links on HDD:", len(scrap.linksOnPage) - len(scrap.checkfiles()), "\n")
    print("You have {} links left to scrap.".format(len(scrap.linksToDownload)))
    print('=======================================================')

    answer = input("Do you want to continue? [Y/N] \n")
    if answer.upper() == "Y":

        print('How many links(stories) you want to download? \n ')
        x = input("all or int \n")
        if x.upper() == "ALL":
            story = scrap.download_list(ran_giv=len(scrap.linksToDownload))
        else:
            story = scrap.download_list(ran_giv=int(x))
    if answer.upper() == 'N':
        print('Do you want to create a dataset?')
        n = input('[Y/N] \n')
        if n.upper() == "Y":
            story = scrap.read_stories_HDD()
        elif n.upper() == 'N':
            print('Done!')
            
    x = input("Create an array of words? [Y/N] \n")
    if x.upper() == 'Y':
        prep = scrap.preparing_stories(story)
        feat_array = scrap.array_words(prep)
        print('=======================================================')
        print('Array of words created! \n')
    else:
        print('Done!')