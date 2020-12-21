# **sentiport**
Super-minimalistic app version of the Data Analysts' sentiment analysis automated reporting 

## **Preview**
![Image](screenshots/sentiport-preview.jpg)

## **1. Project structure**
```
sentiport(root)
│   .env
│   .gitignore
│   app.py
│   config.py
│   docker-compose.yml
│   Dockerfile
│   nltk.txt
│   Procfile
│   README.md
│   requirements.txt
│
├───screenshots
│       sentiport-preview.jpg
│
└───sentiport
    │   forms.py
    │   mail.py
    │   pdf_generator.py
    │   routes.py
    │   __init__.py
    │
    ├───artifacts
    │       artifacts.md
    │
    ├───static
    │       status.js
    │
    ├───templates
    │       404.html
    │       index.html
    │       mail.html
    │       root.html
    │       status.html
    │       success.html
    │
    └───utils
        ├───assets
        │       Closing Page.png
        │       closing_page.png
        │       cover_template.png
        │       Draft Tamplate & Sizing.pdf
        │       executive_summary.png
        │       Extreme Review.png
        │       Get other features template.png
        │       get_other_features.png
        │       Introduction.png
        │       Negative Review.png
        │       Overall Rating Analysis.png
        │       Overall Review Analysis.png
        │       Plain Page Template.png
        │       positive_review.png
        │       review_analysis_by_time.png
        │       review_analysis_by_version.png
        │       review_language_analysis.png
        │       sentiment_analysis.png
        │       table_of_content.png
        │       template_negative_reviews.png
        │
        ├───Helvetica-Font
        │       Helvetica-Bold.ttf
        │       Helvetica-BoldOblique.ttf
        │       helvetica-compressed-5871d14b6903a.otf
        │       helvetica-light-587ebe5a59211.ttf
        │       Helvetica-Oblique.ttf
        │       helvetica-rounded-bold-5871d05ead8de.otf
        │       Helvetica.ttf
        │
        ├───pdf_table_reportlab
        │       bad_good_review.py
        │
        ├───plot_detect_language
        │       detect_language.py
        │
        ├───plot_rating
        │       rating.py
        │
        ├───plot_sentiment_analysis
        │       sentiment_analysis.py
        │
        └───utilities
                crawling.py
                helper.py
```
## **2. How to Run**
### Running the project on local:
#### **Before you run the commands**
  - Make sure you do the commands on the project directory.
  - Create the .env files that contains this environment variables:
    - `FLASK_APP=app.py`
    - `FLASK_ENV=development` #change it to production if you want to deploy it
    - `SECRET_KEY=aDAKSKCMAlzakl321s` #up to you, like password for personal debuging
    - `ST_EMAIL=<your email>` #contact us if you want to use supertype email and password
    - `ST_PASSWORD=<your email's password>` 
    - `REDISCLOUD_URL=<redis cloud url>` #optional if you want to deploy it to heroku, use the url that already given 
  
#### **1. With Docker**
- Install Docker 
  - For Windows without WSL/WSL2:
    - [For Windows Home](https://docs.docker.com/docker-for-windows/install-windows-home/)
    - [For Windows "Above" Home (Enterprise, Professional, etc.)](https://docs.docker.com/docker-for-windows/install/)
  - For Windows with WSL/WSL2(recommended for Windows):
    - [Follow this docs for WSL setup](https://docs.microsoft.com/en-us/windows/wsl/install-win10)
    - [Follow this docs for WSL Docker installation] (https://docs.docker.com/docker-for-windows/wsl/)
  - For Linux
    - [Install Docker](https://docs.docker.com/engine/install/)
    - [Install Docker Compose](https://docs.docker.com/compose/install/)
  - [For Mac](https://docs.docker.com/docker-for-mac/install/)
- Go to sentiport folder
- Build docker images
  -  `docker-compose build` (This will take some time)
- Run the services
  -  `docker-compose up`
  
#### **2. Without Docker**
Coming soon if needed

