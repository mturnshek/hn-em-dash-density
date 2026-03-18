# HN Em-Dash Density

Fetches the last week's worth of text post ShowHNs from Hacker News and ranks every post by its "em-dash density". This is a terrible but perhaps interesting proxy for how much AI was used to write the text.

Em-Dash Density: The percentage of characters in the combined title + body text that are em-dashes (—) or en-dashes (–).

## Usage

```
python3 hn_em_dash_density.py
```

```
# If you want only to only include true — em dash (U+2014) and not – en dash (U+2013)
python3 hn_em_dash_density.py --strictly-em-dashes
```
