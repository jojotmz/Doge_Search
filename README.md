# Doge Search
A search engine that allows users to search for question on Quora or topics on reddit related to a specific query. The search engine shall provide the user an interface for searching, browsing and presenting the results using a basic relevance-feedback implementation.

## 👉 Setup
- All the files used to crawl, scrap and create the solr core are available for download. But you only need the files inside `project website` and `csv` dir. The csv files were obtained by running the python scripts inside the `crawlers` folder. Note to the Quora.py script: Quora's website requires you to update the autenthicated login key, usually by logging in, getting it in the cookies and updating the script.
- I used two main cores for the Engine, one for Quora results the other for Reddit. In order to set them up in solr you must run:
```python
# From your solr installation directory
bin/solr start
# Create the core for Quora
bin/solr create -c quora_core
# Create the core for Reddit
bin/solr create -c reddit_core
# Now create the fields as specified below
bin/post -c quora_core ~/{path_to_quora_csv_file}/Quora_1.csv
bin/post -c reddit_core ~/{path_to_reddit_csv_file}/Reddit_1.csv
```
- Alternatively you can just pick the pre-made cores/collections that I've included in the `Core` dir. Note:
in this case the reddit core is under the name `workpls`, I didn't want to change it to avoid risking any
potential malfunctioning

## 🕷️ Crawlers
In order to run the scripts:
```python
pip install scrapy
scrapy runspider Quora.py
# or
scrapy runspider reddit.py
```

## ☁️ Web UI
No framework were used to elaborate the pages, it's pure html/css/javascript to keep it simple and minimalist. The only important detail is regarding the CORS issue when submitting requests to solr api, its required to either have an extension to your browser that allows you to temporarily disable CORS, or following the steps available [here](http://laurenthinoul.com/how-to-enable-cors-in-solr/)

## 📓 Report
More details available inside the DogeSearch/report/report.pdf file
