<h1 align="center">
    <img alt="StarJeansProj" title="#StarJeans" src="starjeans.png" />
</h1>

<h4 align="center"> 
	🚧 Star Jeans Proj 1.0 🚀 still building... 🚧
</h4>


<p align="center">
  <img alt="GitHub language count" src="https://img.shields.io/github/languages/count/rmendes1/star-jeans?color=%2304D361">

 <img alt="Repository size" src="https://img.shields.io/github/repo-size/rmendes1/star-jeans">
	
  
  <a href="https://github.com/rmendes1/house-rocket/commits/main">
    <img alt="GitHub last commit" src="https://img.shields.io/github/last-commit/rmendes1/star-jeans">
  </a>

  <img alt="License" src="https://img.shields.io/badge/license-MIT-brightgreen">
</p>

# Table of Contents
<p align="center">
  <a href="#description">Description</a> •
  <a href="#dataset">Dataset</a> •
  <a href="#tools">Tools</a> •
  <a href="#steps">Steps</a> •  
  <a href="#conclusion">Conclusion</a> •
  <a href="#next-steps">Next Steps</a> •
  <a href="#license">License</a>
</p>


# **Description**

Star Jeans is a fictional E-commerce company located in the US. Its owners decided to create the company to enter in the country's fashion market selling Jeans for male outfit. The first step is to maintain a low-cost operational system and scale as the customers rate grows up. 
Given the business situation, some important questions must be answered:

1. What is the best price to sell the products?
2. What types of Jeans and colors for the product model?
3. What is the raw material needed?

Star Jeans' main competitors are H&M and Macy's.

# **Dataset**

- The dataset for this project has been extracted from H&M's website's jeans catalog.
- BeautifulSoup was used to extract the showcase products and their respective info (color, size, price, etc.)

| Attributes     | Meaning                                                                                                                                                                                              |
|----------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| product_id             | Unique ID for each item on showcase                                                                                                                                                                         |
| style_id           | First 7 numbers from product_id which identify the jeans style                                                                                                                                                                                |
| color_id          | Last 3 numbers from product_id which identify the jeans color                                                                                                                                                                              |
| product_name       | identifies the jeans model                                                                                                                                                                                   |
| color_name      | identifies the jeans color            |
| fit    | jeans fit                                                                                                                                               |
| product_price       | price in US$                                                                                                                                                                     |
| size_number         | model height in cm                                                                                                                                                                                    |
| size_model     |  Jeans size                                                                                                         |
| cotton           | Cotton percentage                                                                                                                                        |
| polyester      | Polyester percentage                                                                                                                                              |
| spandex          | Spandex percentage |
| elasterell     | Elasterell percentage  |                                                                                                                        
| scrapy_datetime  | Date the scrape was done (it changes every day)  |                                                                                                                        

# Tools
![Python](https://img.shields.io/badge/-Python-007396?style=flat-square&logo=python&logoColor=ffffff)
![SQLite](https://img.shields.io/badge/-SQLite-5CB3FF?style=flat-square&logo=sqlite)

# Steps

- Business understanding
- Data collection via H&M's site
- Webscraping
- Data Cleaning
- Feature Engineering
- Exploratory Data Analysis
- Variable transformation 
- Variable Selection
- ML Algorithm
- Project Deploy on Streamlit Cloud/Heroku Cloud/AWS (to define)

# Conclusion
- TBD
	
	
# Next steps
- Selenium will be used to scrape
- EDA
- Variable Transformation
- Variable Selection
- ML Algorithm to be implemented
- Conclusion

# License

This project is under MIT License.

Done with ❤️ by João Renato Mendes 👋🏽 [Get in touch!](https://www.linkedin.com/in/joaorenatomendes/)

_This readme is in progress_
