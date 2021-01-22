############ NO-COMPILE
# FROM adoptopenjdk:8-jdk-openj9-focal

# COPY requirements.txt sentiport config.py ./myapp/

# WORKDIR /myapp

# # RUN apt update && \
# #     apt upgrade -y && \
# #     apt install -y software-properties-common && \
# #     add-apt-repository -y ppa:deadsnakes/ppa && \
# #     apt install -y python3.7 python3-pip && \
# #     update-alternatives --install /usr/local/bin/python python /usr/bin/python3.7 1 && \
# #     python -m pip install --upgrade pip && \
# #     python -m pip install -r requirements.txt && \
# #     python -m nltk.downloader stopwords && \
# #     python -m spacy download en_core_web_sm

############ PACK
FROM rappdw/docker-java-python:zulu1.8.0_262-python3.7.9

COPY requirements.txt sentiport config.py ./myapp/

WORKDIR /myapp

RUN pip3 install --upgrade pip && \
    pip3 install -r requirements.txt && \
    python -m nltk.downloader stopwords && \
    python -m spacy download en_core_web_sm