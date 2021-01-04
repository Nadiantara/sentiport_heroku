FROM python:3.7

COPY requirements.txt sentiport config.py ./

RUN pip install -r requirements.txt && python -m nltk.downloader stopwords