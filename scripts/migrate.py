#/usr/bin/env python
# coding:utf8

"""
本脚对source/_posts文件页面参数格式化
1. 只保留 title,category 参数
2. 添加 <!--more--> 标签

使用时将下方写入文件部分注释掉
"""

import os
import string

base_dir = os.path.dirname(os.path.dirname(__file__))
posts_dir = os.path.join(base_dir, "_posts")

def parse_post(file_name):
    file_path = os.path.join(posts_dir, file_name)
    parsed_dict = {}
    with open(file_path, "r") as f:
        first_dash = True
        for line in f:
            if not line.strip(): continue
            if "---" in line:
                if first_dash: first_dash = False
                else:
                    return parsed_dict
                continue

            splited = line.split(":")
            if len(splited) < 2:
                print("Error {}".format(splited))
            parsed_dict[splited[0]] = splited[1].strip()

def handle_file(file_name, param):
    print(file_name)
    file_path = os.path.join(posts_dir, file_name)
    with open(file_path, "r+") as f:
        file_content = f.read()
        index = file_content.find("---", 6)
        old_header = file_content[:index+3]
        new_header = "---\n"
        new_header = new_header + "title: " + param.get("title") + "\n"
        if param.get("category"):
            categories = param.get("category")
        else:
            categories = param.get("categories")
        new_header = new_header + "category: " + categories + "\n"
        new_header = new_header + "---"

        file_content = file_content.replace(old_header, "")
        if "<!--more-->" in file_content:
            new_file_content = file_content
        else:
            new_file_content = []
            insert_more_tag = False
            for line in file_content.split("\n"):
                new_file_content.append(line)
                line = line.strip()
                if len(line) < 1: continue
                if line[0] in string.punctuation: continue
                if not insert_more_tag:
                    new_file_content.append("<!--more-->")
                    insert_more_tag = True
            new_file_content = "\n".join(new_file_content)

        new_file_content = new_header  + new_file_content
        print(new_file_content)
        #  f.seek(0)
        #  f.write(new_file_content)
        #  f.truncate()

if __name__ == "__main__":
    files = os.listdir(posts_dir)
    for file_name in files:
        parsed = parse_post(file_name)
        handle_file(file_name, parsed)
