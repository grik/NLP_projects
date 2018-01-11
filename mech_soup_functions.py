import mechanicalsoup
import nltk
from sklearn.feature_extraction.text import CountVectorizer

def filtered_fan_fiction(URL):
    Filters = ('srt', 'lan', 'len', 'p') # list of desired filters
    FilterValues = (3, 1, 0, 2) # list of values for filters  
    FilterSet = ''
    for i in range(len(Filters)):
        FilterSet += '&%s=%d' % (Filters[i], FilterValues[i])
        
    newURL = URL + '?' + FilterSet
    print(newURL)

    return newURL

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

def tokenizing(browser): #function to download and tokenize data 
    soup = browser.get_current_page()
    page = soup.get_text()
    cleaned = cleaning(page)
    tokens = nltk.word_tokenize(str(cleaned))
    text_tokens = nltk.Text(tokens)
    return text_tokens

def preparing_links(browser): #function to prepare (clean) passed list of links, in order to download them  
    l1 = browser.links()
    l2 = []
    links = []
    l4 = []
    l5 = []
    chapters = []
    
    for n in range(len(l1)):
        if 'stitle' in str(l1[n]):
            l2.append(l1[n])
            l4.append(l1[n+1])
            
    for n in l2:
        beglink = str(n).find('href="')
        endlink = str(n).find('"><')
        a = str(n)[beglink+6:endlink]
        links.append(a)
    
    for n in l4:
        beglink = str(n).find('href="')
        endlink = str(n).find('"><')
        a = str(n)[beglink+6:endlink]
        l5.append(a)
        
    for n in l5:
        a = n.split('/')
        chapters.append(a[3])
        
    return links,chapters #list of links to download each fanfic; list of chapters of each fanfic piece
  
def download_list(links,chapters,ran_giv = 1,pr_link=True): #links and chapters are product of preparing_links function; 
    #an_giv is a number of links that are going to be downloaded; for all links  use len(links); 
    #pr_link is a decision whether print links during downloading or not.
    data_sample = []
    
    for n in range(ran_giv):
        old_one = links[n].split('/')
        
        for r in range(int(chapters[n])):
            one_fan_fic = []
            new_one = ''
            old_one[3] = str(r)
            new_one += 'http://fanfiction.net'
            
            for n in range(len(old_one)-1):
                new_one += old_one[n]
                new_one += '/'
            new_one += old_one[-1]
            
            if pr_link == True:
                print(new_one)
                
            browser.open(new_one)
            soup = browser.get_current_page()
            page = soup.get_text()
            cleaned = cleaning(page)
            one_fan_fic.append(cleaned)
        data_sample.append(one_fan_fic)
        
    return data_sample

# The 'following links' steps are redundant, can as well 
# start directly in desired fandom.

browser = mechanicalsoup.StatefulBrowser(raise_on_404 = True)
response = browser.open('http://fanfiction.net')
print(response)

browser.follow_link('movie') 
print(browser.get_url()) # returns a URL

browser.follow_link('Star-Wars')
print(browser.get_url())

filterURL = filtered_fan_fiction(str(browser.get_url()))
browser.open(filterURL) 

links_and_chap = preparing_links(browser)

links = links_and_chap[0]
chapters = links_and_chap[1]

bag = download_list(links,chapters,ran_giv=len(links))
