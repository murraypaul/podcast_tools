# Python 3 server example
# https://pythonbasics.org/webserver/
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

import feedparser
import requests
from lxml import html, etree

#hostName = "http://murraypaul.duckdns.org"
hostName = "localhost"
serverPort = 8081

class MyServer(BaseHTTPRequestHandler):
    def handle_langsam(self):
        origRSS = "https://rss.dw.com/xml/DKpodcast_lgn_de";
        data = feedparser.parse(origRSS);

        self.send_response(200)
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
  <itunes:subtitle>C1 | Deutsch für Profis: Verbessert euer Deutsch mit aktuellen Tagesnachrichten der Deutschen Welle – für Deutschlerner besonders langsam und deutlich gesprochen.<#/itunes:subtitle>
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
             break;

             self.wfile.write(bytes('</item>\n', "utf-8"));
       
        self.wfile.write(bytes('</channel>', "utf-8"));
        self.wfile.write(bytes('</rss>', "utf-8"));

    def handle_langsam_get_item_description(self,feed,item):
        startURL = item.link;
        page = requests.get(startURL);
        tree = html.fromstring(page.content);
        targetURL = tree.xpath('//*[@id="bodyContent"]/div[1]/div[3]/div/div[2]/a/@href')[0];
        print(targetURL);
        page2 = requests.get(targetURL);
        tree2 = html.fromstring(page2.content);
        desc = '\n'.join(tree2.xpath('//*/h2/text()|//*/p/text()'));
        print(desc);

        return desc;

    def do_GET(self):
        if self.path == "/langsam.rss":
            return self.handle_langsam()
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes("<html><head><title>https://pythonbasics.org</title></head>", "utf-8"))
        self.wfile.write(bytes("<p>Request: %s</p>" % self.path, "utf-8"))
        self.wfile.write(bytes("<body>", "utf-8"))
        self.wfile.write(bytes("<p>This is an example web server.</p>", "utf-8"))
        self.wfile.write(bytes("</body></html>", "utf-8"))

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")
