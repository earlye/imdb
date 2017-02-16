# IMDB utility

A very simple IMDB utility that works with IMDB's quick search
service. Basically, if you want to ask IMDB what it
would show in the quick search drop down on its main site, 
type `imdb {query}` and you're in business. If you'd like to
know more details about what it's doing, run `imdb -v {query}`.
If you want to know gory details, run `imdb -vv {query}`.

# Installation

```
git clone git@github.com:/earlye/imdb.git
cd imdb
ln -s $(pwd)/imdb.py {somewhere-on-path}/imdb
```

Or, don't install it, and from wherever you are, run
`{path-to}/imdb.py {query}` instead.

# New Features

_Most Recent Last. Doesn't include bug fixes, or any features I forgot
to list. Maybe that last bit was obvious :-D_

* `-i {glob-filter}` Include only the types specified by `{glob-filter}`
Possible types include:

  - Actor
  - Actress
  - Feature
  - Tv Movie
  - Tv Series
  - Tv Special
  - Video
  - Video Game
