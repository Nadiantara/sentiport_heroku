# Keywords Extractor

This repo contains the script to extract keywords in an app review, as well as returning the reviews mentioning those top keywords.

## Requirements

Requirement | Conda Guide
---|---
Python 3.7.9
Java 8 | [Link](https://anaconda.org/anaconda/openjdk) 
Pandas 
Numpy
TextBlob | [Link](https://anaconda.org/conda-forge/textblob)
Spacy (also download en model) | python -m spacy download en
NLTK
google_play_scraper | pip install google_play_scraper
NLU | pip install nlu pyspark==2.4.7

Make sure to install NLU only after the other requirements have been satisfied.

## More Information

Go to [NLU](https://nlu.johnsnowlabs.com/docs/en/install) to find more detailed documentation on how to install NLU before running on your local.
