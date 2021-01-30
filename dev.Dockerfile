FROM rappdw/docker-java-python:zulu1.8.0_262-python3.7.9

COPY requirements.txt app.py config.py /myapp/
COPY sentiport /myapp/sentiport

WORKDIR /myapp

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    python -m nltk.downloader stopwords && \
    python -m textblob.download_corpora && \
    python -m spacy download en_core_web_sm

CMD gunicorn --bind 0.0.0.0:8000 app
