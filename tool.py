#!/usr/bin/env python3

import argparse
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple
from urllib.parse import quote

tags = ["blockchain", "tech", "web", "linux", "other", "algorithm", "golang", "python", "java", "android"]

image_regex = r"!\[(.*?)\]\((.*?)\)"
link_regex = r"\[(.*?)\]\((.*?)\)"


@dataclass
class Post:
    title: str
    date: str
    tags: List[str]
    draft: bool = False


contents: Dict[str, Post] = {}


def _run(cmd):
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate()
    return (
        stdout.decode("utf-8").strip() if stdout else "",
        stderr.decode("utf-8").strip() if stderr else "",
    )


def push():
    for file in os.listdir("posts"):
        if not file.endswith(".md"):
            raise Exception("Can't push, found file which is not md in posts directory")
    _run(f"git add .")
    _run(f"git commit -m 'Auto commit by script'")
    _run(f"git push")


def collect_all():
    for md in os.listdir("posts"):
        if not md.endswith(".md"):
            continue
        date, *tail = md.split(" ")
        date = datetime.strptime(date, "%Y-%m-%d")
        title = " ".join(tail).replace(".md", "").strip()
        with open(os.path.join("posts", md)) as f:
            lines = f.read().splitlines()
        tags, draft = [], False
        for line in lines[:8]:
            if line.startswith("- tags:"):
                matches = re.findall(link_regex, lines[0])
                tags = [matches[0][0]] if matches else lines[0].replace("tags:", "").strip().split(",")
            elif line.startswith("- draft:"):
                draft = line.replace("- draft:", "").strip().lower() == "true"
        contents[md] = Post(title, date, tags, draft)


def make_post_li(post: Post):
    link = f"/posts/{post.date.strftime('%Y-%m-%d')} {post.title}.md"
    date = post.date.strftime("%b %d, %Y")
    return f"- [{post.title}]({quote(link)}) *{date}*"


def index():
    collect_all()

    # Write tags.md
    tag_contents, readme_tags = [], []
    for tag in tags:
        posts = []
        for post, post in contents.items():
            if tag in post.tags:
                posts.append(post)
        posts.sort(key=lambda x: x.date, reverse=True)
        tag_contents.append(f"## {tag}")
        tag_contents.append(f"{len(posts)} posts")
        readme_tags.append(f"[{tag}({len(posts)})](/tags.md#{tag})")
        for post in posts:
            if post.draft:
                continue
            tag_contents.append(make_post_li(post))
        tag_contents.append("\n")
    with open("tags.md", "w") as f:
        f.write("\n".join(tag_contents))

    # Write README.md
    posts = list(contents.values())
    posts.sort(key=lambda x: x.date, reverse=True)
    readme_contents = []
    for post in posts:
        if post.draft:
            continue
        readme_contents.append(make_post_li(post))
    with open("README.md", "w") as f:
        f.write(" ".join(readme_tags) + "\n\n")
        f.write(f"### *Posts, since 2013*\n\n")
        f.write(f"\n\n")
        f.write("\n".join(readme_contents))


def create_post(title):
    if not title:
        title = input("Please input title: ")
    if not title.strip():
        raise Exception("Title is empty")
    date = datetime.now().strftime("%Y-%m-%d")
    md = os.path.join("posts", f"{date} {title}.md")
    with open(md, "w") as f:
        f.write(f"- tags: \n")
        f.write(f"- date: {date}\n")
        f.write(f"- draft: true\n\n")
        f.write(f"# {title}\n\n")


def publish():
    stdout, stderr = _run(f"git diff --name-only")
    if stderr:
        raise Exception(stderr)
    changed_files = stdout.splitlines()
    print(changed_files)
    for file in changed_files:
        if file.startswith("posts/"):
            # Corret Image path
            print(file)

    index()
    _run(f"git diff")
    char = input("Confirm push (y/n): ")
    if char == "y":
        push()


def create_args_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")
    # push = subparsers.add_parser("push", help="Auto commit and push")
    # index = subparsers.add_parser("index", help="Generate README.md & tags.md")
    new = subparsers.add_parser("new", help="Create a new post")
    new.add_argument("-t", "--title", help="Post title", default=None)
    publish = subparsers.add_parser("publish", help="Check & Publish all posts")
    return parser


if __name__ == "__main__":
    parser = create_args_parser()
    args = parser.parse_args()
    if args.command == "push":
        push()
    elif args.command == "index":
        index()
    elif args.command == "new":
        create_post(args.title)
    elif args.command == "publish":
        publish()
    else:
        parser.print_help()
