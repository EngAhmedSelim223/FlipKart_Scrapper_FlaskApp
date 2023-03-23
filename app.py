from flask import Flask, render_template, redirect, request, jsonify
from flask_cors import CORS,cross_origin
from urllib.request import urlopen as uReq
import requests
from bs4 import BeautifulSoup as bs
import logging
import pymongo

logging.basicConfig(filemode="scrapper.log", level=logging.INFO)
app = Flask(__name__)
@app.route('/', methods = ['GET', 'POST'])
@cross_origin()
# @cross_origin
def home_page():
    
    return render_template('homePage.html')

@app.route('/admin', methods = ['GET','POST'])
@cross_origin()
# @cross_origin
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['pswd']

        if email == "ahmed@gmail.com" and password == "selim":
            result =  render_template('search.html')
        else:
            result =  render_template('homePage.html', output = "You are Not the Admin") 

    return result
@app.route("/review" , methods = ['POST' , 'GET'])
@cross_origin()
# @cross_origin
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['product'].replace(" ","")
            # print(searchString)
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            # print(flipkart_url)
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.find_all("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    logging.info("name")

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))

            
            
            client = pymongo.MongoClient("mongodb+srv://Ahmed1995:ahmedselim@cluster0.fueswnp.mongodb.net/?retryWrites=true&w=majority")
            db = client['FlipKart']

            coll_pw_eng = db['scraper_flipkart']
            coll_pw_eng.insert_many(reviews)

            return render_template('results.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('search.html')



    

if __name__ == "__main__":
    app.run(host="0.0.0.0")