FROM rappdw/docker-java-python:zulu1.8.0_262-python3.7.9

COPY requirements.txt sentiport config.py ./myapp/

WORKDIR /myapp

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    python -m nltk.downloader stopwords && \
    python -m spacy download en_core_web_sm