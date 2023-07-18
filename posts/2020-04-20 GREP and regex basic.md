- tags: [linux](/tags.md#linux)
- date: 2020-04-20

# GREP and regex basic

`GREP` is global regular expression print. It may the most popular tool to find patterns in file and it is always a built-in command in *nix system. We can see it from name that grep can match string from input data with regular expression. In this article, I'll show you how to use grep and some normal regular expression meanings in daily scenario.

Overall usage of grep

```bash
grep [options] regex FILE_PATTERNS

```

## Some common options

- **-i**: case INSENSITIVE search
- **-w**: check for full words, not for sub-string
- **-B,-A,-C**: show context before,after,around the mathching case
- **-r**: searching in all files recursively
- **-v**: invert match, show all line that do not match the regex
- **-c**: count number of matches
- **-l**: display only the file names
- **-o**: show only the matched string, not all line
- **-n**: show line numbers while displaying the output

## several repeatition operators

- **?** is optional and at most once
- ***** will be matched zero or more times
- **+** will be matched one or more times
- **{n}** will be matched exactly n times
- **{n,}** will be matched n or more times
- **{,m}** will be matched at most m times
- **{n, m}** will be matched at least n times, but not more than m times