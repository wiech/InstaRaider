#!/usr/bin/env python
"""
instaRaider.py

@amirkurtovic

"""

from bs4 import BeautifulSoup
import selenium.webdriver as webdriver
import re
from time import sleep
import urllib
import urllib2
import os
import sys

class instaRaider(object):

    def getImageCount(self, url):
        '''
        Given a url to Instagram profile, return number of photos posted
        '''
        response = urllib2.urlopen(url)
        countsCode = re.search(r'counts\":{\"media\":\d+', response.read())
        count = re.findall(r'\d+', countsCode.group())
        return count[0]

    def loadInstagram(self, profileUrl):
        '''
        Using Selenium WebDriver, load Instagram page to get page source
    
        '''
        count = self.getImageCount(self.profileUrl)
        print self.userName + " has " + str(count) + " photos on Instagram."

        print "Loading Selenium WebDriver..."
        driver = webdriver.Firefox()
        driver.get(self.profileUrl)
        driver.implicitly_wait(self.PAUSE)

        print "Loading Instagram profile..."

        clicks = (int(count)-60)/20+1

        for x in range(3):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sys.stdout.write('.')
            sys.stdout.flush()
            sleep(self.PAUSE)
    
        # Click on "Load more..." label
        element = driver.find_element_by_xpath(self.loadLabelXPATH)

        for y in range(clicks):
            element.click()
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sys.stdout.write('.')
            sys.stdout.flush()
            sleep(self.PAUSE)
     
        # After load all profile photos, retur source to getPhotos()
        source = BeautifulSoup(driver.page_source)
        return source

    def validUser(self, userName):
        '''
        returns True if Instagram username is valid
        '''
        # check if Instagram username is valid
        req = urllib2.Request(self.profileUrl)

        try:
            urllib2.urlopen(req)
        except:
            return False
        # if req doesn't fail, user profile exists
        return True

    def photoExists(self, url):
        '''
        Returns true if photo exists
        Used when checking which suffix Instagram used for full-res photo
        url: URL to Instagram photo
        '''
        try:
            urllib2.urlopen(profileUrl)
        except:
            return False
    
        return True


    def getPhotos(self, source, userName, count):
        '''
        Given source code for loaded Instagram page,
        extract all hrefs and download full-resolution photos
    
        source: HTML source code of Instagram profile papge
        '''
        # directory where photos will be saved
        directory = './Images/' + userName + '/'
        
        # logfile to store urls is csv format
        logfile = userName + '.csv'
        file = open(logfile, "a")

        # check if directory exists, if not, make it
        if not os.path.exists(directory):
            os.makedirs(directory)
    
        # photo number for file names
        photoNumber = 0
    
        # indexes for progress bar
        photosSaved = 0
        progressBar = 0

    
        print "\nRaiding Instagram..."
        print "Saving photos to " + directory
        
        # TODO: Fix formatting issue
        timeToSave = str(count/60) + ":" + str(count%60)
        print "This could take " + timeToSave + "."
        
        print "------"
        # print progress bar
        print "Photos saved so far:"
        print "     ---------10--------20--------30--------40--------50"
        sys.stdout.write(str(progressBar) + "    ")
        sys.stdout.flush()
    
        for x in source.findAll('li', {'class':'photo'}):
    
            if (photoNumber >= count):
                break
            else:
                # increment photonumber for next image
                photoNumber += 1
            
                #extract url to thumbnail from each photo
                rawUrl = re.search(r'url\(\"https?://[^\s<>"]+|www\.[^\s<>"]+', str(x))
    
                # format thumbnail url to lead to full-resolution photo
                # Instagram full-res URLs end in suffixes stored in fullResSuffixes list
                photoUrl = str(rawUrl.group())[5:-5]
                suffix = ''
                for item in self.fullResSuffixes:
                    url = photoUrl + item
                    if(self.photoExists(url)):
                        suffix = item
    
                photoUrl = str(rawUrl.group())[5:-5] + suffix
                photoName = directory + userName + "_" + str(photoNumber) + '.jpg'

                # save full-resolution photo
                urllib.urlretrieve(photoUrl, photoName)
                
                # save filename and url to CSV file
                file.write(photoUrl + "," + photoName + "\n")
            
                # print hash to progress bar
                if (photosSaved == 50):
                    photosSaved = 1
                    progressBar += 50
                    sys.stdout.write('\n' + str(progressBar) + ' ')
                    sys.stdout.write('#')
                    sys.stdout.flush()
                
                else:
                    # increment progress bar
                    photosSaved += 1
                    sys.stdout.write('#')
                    sys.stdout.flush()
                

                sleep(self.PAUSE)

        print "\n------"
        print "Saved " + str(photoNumber) + " images to " + directory
        
        # close logfile
        file.close()
        print "Saved activity in logfile: " + logfile
    
    
    def __init__(self, userName):
        self.userName = userName
        self.profileUrl = 'http://instagram.com/' + userName + '/'
        self.count = self.getImageCount(self.profileUrl)
        self.fullResSuffixes = ['7.jpg', '8.jpg', 'n.jpg']
        self.PAUSE = 1
        self.loadLabelXPATH = "//html/body/span/div/div/div/section/div/span/a/span[2]/span/span"
