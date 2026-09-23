#!/usr/bin/env python3
import urllib.parse
MID = "52880"
TRACK = "Br7kCmfVLtE"
OFFER = "1539873.528809996565778384071734"

def make_link(url):
    return "https://click.linksynergy.com/link?id=" + TRACK + "&offerid=" + OFFER + "&type=2&murl=" + urllib.parse.quote(url)

url1 = "https://www.rboutique.com/en-us/products/cashmere-blend-turtleneck-sweater-piacenza-1733-39895"
url2 = "https://www.rboutique.com/en-us/products/stretch-canvas-j06-pants-emporio-armani-35443"

path = r"C:\Users\HP\AppData\Local\hermes\rboutique-affiliate\site\index.html"
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old1 = "' + make_tracked_link(products[0]['url']) + '"
old2 = "' + make_tracked_link(products[1]['url']) + '"
content = content.replace(old1, make_link(url1))
content = content.replace(old2, make_link(url2))

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed links in index.html")
print("Link 1:", make_link(url1)[:90])
print("Link 2:", make_link(url2)[:90])
