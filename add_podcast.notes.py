from http.server import BaseHTTPRequestHandler, HTTPServer
import time

import feedparser
import requests
from lxml import html, etree
import pickle
from shutil import copyfile
from pathlib import Path

#hostName = "http://murraypaul.duckdns.org"
hostName = "localhost"
serverPort = 8081

DescCache = {}
ConfigFolder = Path(".podcast-toolbox")

class MyServer(BaseHTTPRequestHandler):
    def handle_langsam(self):
        origRSS = "https://rss.dw.com/xml/DKpodcast_lgn_de";
        data = feedparser.parse(origRSS);

        self.send_response(200)
        self.send_header("Content-type", "application/rss+xml; charset=UTF-8")
        self.end_headers()
        
        self.wfile.write(bytes('<?xml version="1.0" encoding="UTF-8"?>\n', "utf-8"));
        self.wfile.write(bytes('<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:georss="http://www.georss.org/georss" xmlns:atom="http://www.w3.org/2005/Atom">', "utf-8"));

        self.wfile.write(bytes('<channel>', "utf-8"));
        self.wfile.write(bytes('<title>' + data.feed.title + '</title>', "utf-8"));
        self.wfile.write(bytes('<link>http://' + hostName + ':' + str(serverPort) + '/' + self.path + '</link>', "utf-8"));
        self.wfile.write(bytes('<description>' + data.feed.description + '</description>', "utf-8"));
        self.wfile.write(bytes('<language>' + data.feed.language + '</language>', "utf-8"));
        self.wfile.write(bytes('<copyright>' + data.feed.copyright + '</copyright>', "utf-8"));
        self.wfile.write(bytes('<pubDate>' + data.feed.published + '</pubDate>', "utf-8"));
        self.wfile.write(bytes('<image>', "utf-8"));
        self.wfile.write(bytes('<url>' + data.feed.image.href + '</url>', "utf-8"));
#        self.wfile.write(bytes('<title>' + data.feed.image.title + '</title>', "utf-8"));
#        self.wfile.write(bytes('<link>' + data.feed.image.link + '</link>', "utf-8"));
        self.wfile.write(bytes('</image>', "utf-8"));
        self.wfile.write(bytes('''
  <itunes:block>no</itunes:block>
  <itunes:explicit>clean</itunes:explicit>
  <itunes:author>DW.COM | Deutsche Welle</itunes:author>
  <itunes:owner>
   <itunes:name>DW.COM | Deutsche Welle</itunes:name>
   <itunes:email>podcasts@dw.com</itunes:email>
  </itunes:owner>
  <itunes:subtitle>C1 | Deutsch für Profis: Verbessert euer Deutsch mit aktuellen Tagesnachrichten der Deutschen Welle – für Deutschlerner besonders langsam und deutlich gesprochen.</itunes:subtitle>
  <itunes:summary>C1 | Deutsch für Profis: Verbessert euer Deutsch mit aktuellen Tagesnachrichten der Deutschen Welle – für Deutschlerner besonders langsam und deutlich gesprochen.</itunes:summary>
  <itunes:category text="Education">
   <itunes:category text="Language Learning"/>
  </itunes:category>
  <ttl>10</ttl>\n''', "utf-8"));

        for item in data.entries:
             self.wfile.write(bytes('<item>', "utf-8"));

             self.wfile.write(bytes('<guid isPermaLink="false">' + item.id + '</guid>', "utf-8"));
             self.wfile.write(bytes('<pubDate>' + item.published + '</pubDate>', "utf-8"));
             self.wfile.write(bytes('<title>' + item.title + '</title>', "utf-8"));
             self.wfile.write(bytes('<link>' + item.link + '</link>', "utf-8"));
             self.wfile.write(bytes('<description>' + self.handle_langsam_get_item_description(data.feed,item) + '</description>', "utf-8"));
             self.wfile.write(bytes('<category>' + item.category + '</category>', "utf-8"));
             self.wfile.write(bytes('''
   <itunes:author>DW.COM | Deutsche Welle</itunes:author>
   <itunes:keywords>Deutsch lernen</itunes:keywords>
   <itunes:explicit>clean</itunes:explicit>\n''', "utf-8"));
             if len(item.enclosures) > 0:
                 self.wfile.write(bytes('<enclosure url="' + item.enclosures[0].href + '" type="' + item.enclosures[0].type + '" length="' + item.enclosures[0].length + '"/>\n', "utf-8"));
#             self.wfile.write(bytes('<itunes:duration></itunes:duration>', "utf-8"));
#             break;

             self.wfile.write(bytes('</item>\n', "utf-8"));
       
        self.wfile.write(bytes('</channel>', "utf-8"));
        self.wfile.write(bytes('</rss>', "utf-8"));

    def handle_langsam_get_item_description(self,feed,item):
        startURL = item.link;
        desc = self.get_desc_from_cache(startURL);
        if desc == "":
            page = requests.get(startURL);
            tree = html.fromstring(page.content);
            targetURL = "";
            try:
                targetURL = tree.xpath('//*[@id="bodyContent"]/div[1]/div[3]/div/div[2]/a/@href')[0];
            except Exception as err:
                print(f"Exception in tree.xpath: {err=}, {type(err)=}");
                print("While handling: " + startURL);
                return "";
            page2 = requests.get(targetURL);
            tree2 = html.fromstring(page2.content);
            desc = '\n\n'.join(tree2.xpath('//*/h2/text()|//*/p/text()'));
            if desc != "":
                self.add_desc_to_cache(startURL,desc);
            else:
                print("No description found for: " + startURL);

        return desc;

    def handle_topthema(self):
        origRSS = "http://rss.dw.com/xml/DKpodcast_topthemamitvokabeln_de";
        data = feedparser.parse(origRSS);

        self.send_response(200)
        self.send_header("Content-type", "application/rss+xml; charset=UTF-8")
        self.end_headers()
        
        self.wfile.write(bytes('<?xml version="1.0" encoding="UTF-8"?>\n', "utf-8"));
        self.wfile.write(bytes('<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:georss="http://www.georss.org/georss" xmlns:atom="http://www.w3.org/2005/Atom">', "utf-8"));

        self.wfile.write(bytes('<channel>', "utf-8"));
        self.wfile.write(bytes('<title>' + data.feed.title + '</title>', "utf-8"));
        self.wfile.write(bytes('<link>http://' + hostName + ':' + str(serverPort) + '/' + self.path + '</link>', "utf-8"));
        self.wfile.write(bytes('<description>' + data.feed.description + '</description>', "utf-8"));
        self.wfile.write(bytes('<language>' + data.feed.language + '</language>', "utf-8"));
        self.wfile.write(bytes('<copyright>' + data.feed.copyright + '</copyright>', "utf-8"));
        self.wfile.write(bytes('<pubDate>' + data.feed.published + '</pubDate>', "utf-8"));
        self.wfile.write(bytes('<image>', "utf-8"));
        self.wfile.write(bytes('<url>' + data.feed.image.href + '</url>', "utf-8"));
#        self.wfile.write(bytes('<title>' + data.feed.image.title + '</title>', "utf-8"));
#        self.wfile.write(bytes('<link>' + data.feed.image.link + '</link>', "utf-8"));
        self.wfile.write(bytes('</image>', "utf-8"));
        self.wfile.write(bytes('''
  <itunes:block>no</itunes:block>
  <itunes:explicit>clean</itunes:explicit>
  <itunes:author>DW.COM | Deutsche Welle</itunes:author>
  <itunes:owner>
   <itunes:name>DW.COM | Deutsche Welle</itunes:name>
   <itunes:email>podcasts@dw.com</itunes:email>
  </itunes:owner>
  <itunes:subtitle>B1 | Deutsch für Fortgeschrittene: Deutsch lernen mit Realitätsbezug: aktuelle Berichte der Deutschen Welle – leicht verständlich und mit Vokabelglossar.</itunes:subtitle>
  <itunes:summary>B1 | Deutsch für Fortgeschrittene: Deutsch lernen mit Realitätsbezug: aktuelle Berichte der Deutschen Welle – leicht verständlich und mit Vokabelglossar.</itunes:summary>
  <itunes:category text="Education">
   <itunes:category text="Language Learning"/>
  </itunes:category>
  <ttl>10</ttl>\n''', "utf-8"));

        for item in data.entries:
             self.wfile.write(bytes('<item>', "utf-8"));

             self.wfile.write(bytes('<guid isPermaLink="false">' + item.id + '</guid>', "utf-8"));
             self.wfile.write(bytes('<pubDate>' + item.published + '</pubDate>', "utf-8"));
             self.wfile.write(bytes('<title>' + item.title + '</title>', "utf-8"));
             self.wfile.write(bytes('<link>' + item.link + '</link>', "utf-8"));
             self.wfile.write(bytes('<description>' + self.handle_topthema_get_item_description(data.feed,item) + '</description>\n', "utf-8"));
             self.wfile.write(bytes('<category>' + item.category + '</category>', "utf-8"));
             self.wfile.write(bytes('''
   <itunes:author>DW.COM | Deutsche Welle</itunes:author>
   <itunes:keywords>Deutsch lernen</itunes:keywords>
   <itunes:explicit>clean</itunes:explicit>\n''', "utf-8"));
             if len(item.enclosures) > 0:
                 self.wfile.write(bytes('<enclosure url="' + item.enclosures[0].href + '" type="' + item.enclosures[0].type + '" length="' + item.enclosures[0].length + '"/>\n', "utf-8"));
             self.wfile.write(bytes('<itunes:duration>' + item.itunes_duration + '</itunes:duration>', "utf-8"));

             self.wfile.write(bytes('</item>\n', "utf-8"));
       
        self.wfile.write(bytes('</channel>', "utf-8"));
        self.wfile.write(bytes('</rss>', "utf-8"));

    def handle_topthema_get_item_description(self,feed,item):
        startURL = item.link;
        desc = self.get_desc_from_cache(startURL);
        if desc == "":
            page = requests.get(startURL);
            tree = html.fromstring(page.content);
            targetURL = "";
            results = [];
            #Two forms, one with text on separate page, one embedded
            test = tree.xpath('//*[@class="start-lecture"]/a/@href');
            if len(test) == 0:
                results = tree.xpath('//*[@id="dkELearning"]/div[4]/p//text()[not(ancestor::span[@class="bubbleText"])]|//*[@id="dkELearning"]/div[4]/p//br[not(ancestor::span[@class="bubbleText"])]');
                for result in results:
                    if isinstance(result,str):
                        desc = desc + result;
                    else:
                        desc = desc + "\n";
            else:
                targetURL = test[0]
                if targetURL[0] == "/":
                    targetURL = "https://learngerman.dw.com/" + targetURL;
                page2 = requests.get(targetURL);
                tree2 = html.fromstring(page2.content);
                results = tree2.xpath('//*/div[@class="content"]/div/span/*');
                for line in results:
                    desc = desc + line.text_content() + "\n\n";
            if desc != "":
                self.add_desc_to_cache(startURL,desc);
            else:
                print("No description found for: " + startURL);

        return desc;


    def handle_wortedewoche(self):
        origRSS = "http://rss.dw-world.de/xml/DKpodcast_wortderwoche_de";
        data = feedparser.parse(origRSS);

        self.send_response(200)
        self.send_header("Content-type", "application/rss+xml; charset=UTF-8")
        self.end_headers()
        
        self.wfile.write(bytes('<?xml version="1.0" encoding="UTF-8"?>\n', "utf-8"));
        self.wfile.write(bytes('<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:georss="http://www.georss.org/georss" xmlns:atom="http://www.w3.org/2005/Atom">', "utf-8"));

        self.wfile.write(bytes('<channel>', "utf-8"));
        self.wfile.write(bytes('<title>' + data.feed.title + '</title>', "utf-8"));
        self.wfile.write(bytes('<link>http://' + hostName + ':' + str(serverPort) + '/' + self.path + '</link>', "utf-8"));
        self.wfile.write(bytes('<description>' + data.feed.description + '</description>', "utf-8"));
        self.wfile.write(bytes('<language>' + data.feed.language + '</language>', "utf-8"));
        self.wfile.write(bytes('<copyright>' + data.feed.copyright + '</copyright>', "utf-8"));
        self.wfile.write(bytes('<pubDate>' + data.feed.published + '</pubDate>', "utf-8"));
        self.wfile.write(bytes('<image>', "utf-8"));
        self.wfile.write(bytes('<url>' + data.feed.image.href + '</url>', "utf-8"));
#        self.wfile.write(bytes('<title>' + data.feed.image.title + '</title>', "utf-8"));
#        self.wfile.write(bytes('<link>' + data.feed.image.link + '</link>', "utf-8"));
        self.wfile.write(bytes('</image>', "utf-8"));
        self.wfile.write(bytes('''
  <itunes:block>no</itunes:block>
  <itunes:explicit>clean</itunes:explicit>
  <itunes:author>DW.COM | Deutsche Welle</itunes:author>
  <itunes:owner>
   <itunes:name>DW.COM | Deutsche Welle</itunes:name>
   <itunes:email>podcasts@dw.com</itunes:email>
  </itunes:owner>
  <itunes:subtitle>B2 | Deutsch für Fortgeschrittene: Ein Format für die Frühstückspause – lernt jede Woche ein neues kurioses Wort und seine Bedeutung in einer Minute kennen.</itunes:subtitle>
  <itunes:summary>B2 | Deutsch für Fortgeschrittene: Ein Format für die Frühstückspause – lernt jede Woche ein neues kurioses Wort und seine Bedeutung in einer Minute kennen.</itunes:summary>
  <itunes:category text="Education">
   <itunes:category text="Language Learning"/>
  </itunes:category>
  <ttl>10</ttl>\n''', "utf-8"));

        count = 0;
        for item in data.entries:
             self.wfile.write(bytes('<item>', "utf-8"));

             self.wfile.write(bytes('<guid isPermaLink="false">' + item.id + '</guid>', "utf-8"));
             self.wfile.write(bytes('<pubDate>' + item.published + '</pubDate>', "utf-8"));
             self.wfile.write(bytes('<title>' + item.title + '</title>', "utf-8"));
             self.wfile.write(bytes('<link>' + item.link + '</link>', "utf-8"));
             self.wfile.write(bytes('<description>' + self.handle_wortedewoche_get_item_description(data.feed,item) + '</description>', "utf-8"));
             self.wfile.write(bytes('<category>' + item.category + '</category>', "utf-8"));
             self.wfile.write(bytes('''
   <itunes:author>DW.COM | Deutsche Welle</itunes:author>
   <itunes:keywords>Deutsch lernen</itunes:keywords>
   <itunes:explicit>clean</itunes:explicit>\n''', "utf-8"));
             if len(item.enclosures) > 0:
                 self.wfile.write(bytes('<enclosure url="' + item.enclosures[0].href + '" type="' + item.enclosures[0].type + '" length="' + item.enclosures[0].length + '"/>\n', "utf-8"));
#             self.wfile.write(bytes('<itunes:duration></itunes:duration>', "utf-8"));
             count = count + 1
             if count > 2:
                 break;

             self.wfile.write(bytes('</item>\n', "utf-8"));
       
        self.wfile.write(bytes('</channel>', "utf-8"));
        self.wfile.write(bytes('</rss>', "utf-8"));

    def handle_wortedewoche_get_item_description(self,feed,item):
        startURL = item.link;
        #Seem to get 404 with ? portion included, for some words only
        if "?" in startURL:
            startURL = startURL[:startURL.index("?")]
        desc = self.get_desc_from_cache(startURL);
        if desc == "":
            page = requests.get(startURL);
            tree = html.fromstring(page.content);
            desc = '\n\n'.join(tree.xpath('//*/div[@id="bodyContent"]/*/h1/text()|//*/div[@id="bodyContent"]/*/p[@class="intro"]/text()|//*[@id="bodyContent"]/div[1]/div[4]/div/p/text()'));
#            print(startURL);
#            print(desc);
            if desc != "":
                self.add_desc_to_cache(startURL,desc);
            else:
                print("No description found for: " + startURL);

        return desc;

    def handle_nachrichtenleicht(self):
        origRSS = "https://www.nachrichtenleicht.de/nachrichtenpodcast-100.xml";
        data = feedparser.parse(origRSS);

        self.send_response(200)
        self.send_header("Content-type", "application/rss+xml; charset=UTF-8")
        self.end_headers()
        
        self.wfile.write(bytes('<?xml version="1.0" encoding="UTF-8"?>\n', "utf-8"));
        self.wfile.write(bytes('<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:georss="http://www.georss.org/georss" xmlns:atom="http://www.w3.org/2005/Atom">', "utf-8"));

        self.wfile.write(bytes('<channel>', "utf-8"));
        self.wfile.write(bytes('<title>' + data.feed.title + '</title>', "utf-8"));
        self.wfile.write(bytes('<link>http://' + hostName + ':' + str(serverPort) + '/' + self.path + '</link>', "utf-8"));
        self.wfile.write(bytes('<description>' + data.feed.description + '</description>', "utf-8"));
        self.wfile.write(bytes('<language>' + data.feed.language + '</language>', "utf-8"));
        self.wfile.write(bytes('<copyright>' + data.feed.copyright + '</copyright>', "utf-8"));
        self.wfile.write(bytes('<pubDate>' + data.feed.published + '</pubDate>', "utf-8"));
        self.wfile.write(bytes('<image>', "utf-8"));
        self.wfile.write(bytes('<url>' + data.feed.image.href + '</url>', "utf-8"));
#        self.wfile.write(bytes('<title>' + data.feed.image.title + '</title>', "utf-8"));
#        self.wfile.write(bytes('<link>' + data.feed.image.link + '</link>', "utf-8"));
        self.wfile.write(bytes('</image>', "utf-8"));
        self.wfile.write(bytes('''
  <itunes:explicit>No</itunes:explicit>
  <itunes:author>Deutschlandfunk Nachrichtenleicht</itunes:author>
  <itunes:owner>
   <itunes:name>Redaktion deutschlandradio.de</itunes:name>
   <itunes:email>hoererservice@deutschlandradio.de</itunes:email>
  </itunes:owner>
  <itunes:subtitle>Die Beiträge zur Sendung</itunes:subtitle>
  <ttl>10</ttl>\n''', "utf-8"));

        for item in data.entries:
             self.wfile.write(bytes('<item>', "utf-8"));

             self.wfile.write(bytes('<guid isPermaLink="false">' + item.id + '</guid>', "utf-8"));
             self.wfile.write(bytes('<pubDate>' + item.published + '</pubDate>', "utf-8"));
             self.wfile.write(bytes('<title>' + item.title + '</title>', "utf-8"));
             self.wfile.write(bytes('<link>' + item.link + '</link>', "utf-8"));
             self.wfile.write(bytes('<description>' + self.handle_nachrichtenleicht_get_item_description(data.feed,item) + '</description>', "utf-8"));
             if 'category' in item:
                 self.wfile.write(bytes('<category>' + item.category + '</category>', "utf-8"));
             self.wfile.write(bytes('''
   <itunes:author>Deutschlandfunk Nachrichtenleicht</itunes:author>''',"utf-8"));
             if len(item.enclosures) > 0:
                 self.wfile.write(bytes('<enclosure url="' + item.enclosures[0].href + '" type="' + item.enclosures[0].type + '" length="' + item.enclosures[0].length + '"/>\n', "utf-8"));
#             self.wfile.write(bytes('<itunes:duration></itunes:duration>', "utf-8"));
#             break;

             self.wfile.write(bytes('</item>\n', "utf-8"));
       
        self.wfile.write(bytes('</channel>', "utf-8"));
        self.wfile.write(bytes('</rss>', "utf-8"));

    def handle_nachrichtenleicht_get_item_description(self,feed,item):
        startURL = item.link;
        desc = self.get_desc_from_cache(startURL);
        if desc == "":
            page = requests.get(startURL);
            tree = html.fromstring(page.content);
            desc = '\n\n'.join(tree.xpath('//*[@id="main-app"]/main/div/article/header/h1[@class="b-article-header-main"]/text()|//*[@id="main-app"]/main/div/article/header/p[@class="article-header-description"]/text()|//*[@id="main-app"]/main/div/article/div/section[@class="b-article-details"]/div/text()'));
#            print(startURL);
#            print(desc);
            if desc != "":
                self.add_desc_to_cache(startURL,desc);
            else:
                print("No description found for: " + startURL);

        return desc;

    def do_GET(self):
        if self.path == "/langsam.rss":
            return self.handle_langsam()
        elif self.path == "/topthema.rss":
            return self.handle_topthema()
        elif self.path == "/wortedewoche.rss":
            return self.handle_wortedewoche()
        elif self.path == "/nachrichtenleicht.rss":
            return self.handle_nachrichtenleicht()
        else:
            self.send_response(404)
            self.end_headers()

    def get_desc_from_cache(self,startURL):
        global DescCache
        if len(DescCache) == 0:
            try:
                with open(ConfigFolder / 'desccache.pickle','rb') as cachefile:
                    DescCache = pickle.load(cachefile)
            except FileNotFoundError:
                pass

        if startURL in DescCache:
            return DescCache[startURL]
        else:
            return ""

    def add_desc_to_cache(self,startURL,desc):
        DescCache[startURL] = desc;
        try:
            copyfile(ConfigFolder / 'desccache.pickle',ConfigFolder / 'desccache.bak')
        except FileNotFoundError:
            pass
        try:
            with open(ConfigFolder / 'desccache.pickle','wb') as cachefile:
                pickle.dump(DescCache,cachefile)

            print(f"Wrote {len(DescCache)} entries to desc cache file.")
        except:
            print("Error writing Desc cache file, restoring backup")
            copyfile(ConfigFolder / 'desccache.pickle',ConfigFolder / 'desccache.txt')

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
