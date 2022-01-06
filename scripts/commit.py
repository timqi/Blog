#!/usr/bin/env python
# coding:utf8

"""
在 README.md 中生成文章索引

参数解释：
./scripts/commit.py # 正常部署
./scripts/commit.py clean # 清空git历史记录
"""

import os
import sys
import string
import datetime

base_dir = os.path.dirname(os.path.dirname(__file__))
posts_dir = os.path.join(base_dir, "_posts")
BASE_URL = "https://www.timqi.com"


def get_date(item):
    return item.get("date")

def get_title_of_file(file_name):
    with open(os.path.join(posts_dir, file_name), "r") as f:
        for line in f:
            if line.split(":")[0] == "title":
                return line.split(":")[1].strip()

def get_post_objs():
    posts = os.listdir(posts_dir)
    post_obj_arr = []
    for post in posts:
        file_name = post
        post = post.replace(".md", "")
        post_items = post.split("-")
        if len(post_items) < 4:
            print("Error of post name: %s" % post)
        year, month, day = post_items[0], post_items[1], post_items[2]
        url_title = "-".join(post_items[3:])
        post_obj_arr.append({
            "date": datetime.date(int(year), int(month), int(day)),
            "file_name": file_name,
            "title": get_title_of_file(file_name),
            "url_title": url_title,
            "url": "/".join([BASE_URL, year, month, day, url_title]) + "/"
        })
    post_obj_arr.sort(key=get_date, reverse=True)
    return post_obj_arr

def get_readme(post_objs):
    README = "source files of site [https://www.timqi.com](https://www.timqi.com), %s posts since 09.29 2013\n\n" % len(post_objs)
    for p in post_objs:
        README = README + "- [%s](%s)\n" % (p.get("title"), p.get("url"))
    return README

if __name__ == "__main__":
    post_objs = get_post_objs()
    README = get_readme(post_objs)

    with open(os.path.join(base_dir, "README.md"), "w") as f:
        f.write(README)

    if sys.argv[1] == 'clean':
        os.system("cd %s && git checkout --orphan tmp_master && git add . && git commit -m 'Clean Deploy' && git branch -D master && git branch -m master && git push -f origin master" % base_dir)
    else:
        os.system("cd %s && git add . && git commit -m 'Update' && git push" % base_dir)
