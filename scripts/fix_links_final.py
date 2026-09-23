import urllib.parse, os
TRACK="Br7kCmfVLtE"; OFFER="1539873.528809996565778384071734"
url1="https://www.rboutique.com/en-us/products/cashmere-blend-turtleneck-sweater-piacenza-1733-39895"
url2="https://www.rboutique.com/en-us/products/stretch-canvas-j06-pants-emporio-armani-35443"
link1="https://click.linksynergy.com/link?id="+TRACK+"&offerid="+OFFER+"&type=2&murl="+urllib.parse.quote(url1)
link2="https://click.linksynergy.com/link?id="+TRACK+"&offerid="+OFFER+"&type=2&murl="+urllib.parse.quote(url2)
path="C:\\Users\\HP\\AppData\\Local\\hermes\\rboutique-affiliate\\site\\index.html"
with open(path,"r",encoding="utf-8") as f: c=f.read()
c=c.replace("' + make_tracked_link(products[0]['url']) + '", link1)
c=c.replace("' + make_tracked_link(products[1]['url']) + '", link2)
with open(path,"w",encoding="utf-8") as f: f.write(c)
print("Fixed 2 links")
