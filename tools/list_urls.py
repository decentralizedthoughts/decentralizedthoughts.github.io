#!/usr/bin/env python3
import os, glob

root="_site"
urls=[]

def add(u):
    if u not in urls:
        urls.append(u)

# stable pages
for p in ["", "tags/", "start-here/", "course/", "videos/", "feed.xml"]:
    fp = os.path.join(root, p, "index.html") if p.endswith("/") else os.path.join(root, p)
    if os.path.exists(fp):
        add("/"+p)

# pagination pages if present
for p in sorted(glob.glob(os.path.join(root, "page*/index.html"))):
    rel = p[len(root):].replace("/index.html","/")
    add(rel)

# about pages
for p in sorted(glob.glob(os.path.join(root, "about-*/index.html"))):
    rel = p[len(root):].replace("/index.html","/")
    add(rel)

# posts: sample across time, 1 per year if possible
posts = sorted(glob.glob(os.path.join(root, "20??-??-??-*/index.html")))
by_year={}
for p in posts:
    year=os.path.basename(os.path.dirname(p))[:4]
    by_year.setdefault(year, []).append(p)
for year in sorted(by_year.keys()):
    plist=by_year[year]
    pick=plist[len(plist)//2]
    rel = pick[len(root):].replace("/index.html","/")
    add(rel)

print("\n".join(urls))
