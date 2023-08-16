# Library-parser #

## Description ##

The script in the repository parse data from the [tululu.org](https://tululu.org/) site by book IDs.

## How to install? ##

Python3 should be already installed. 
Then use `pip` (or `pip3` for Python3) to install dependencies:

```commandline
pip install -r requirements.txt
```

Recommended using [virtualenv/venv](https://docs.python.org/3/library/venv.html)

## Launch ##
1) Add to `.env` file:
   - `WD` - The path to the directory where you will download books and images
2) Run the script by selecting the IDs for books and pictures that will be downloaded:
  ```commandline
  python tululu.py -s 10 -e 20
  ```

## Project Goals ##

The code is written for educational purposes - for a course on Python and web development on the [Devman](https://dvmn.org).
