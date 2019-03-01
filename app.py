from flask import Flask, render_template, jsonify, redirect
from flask_pymongo import PyMongo
import scrape_mars

import scrape_mars

app = Flask(__name__)
mongo = PyMongo(app)

# Create connection variable
#conn = 'mongodb://localhost:5000'
# Use PyMongo to establish Mongo connection
app.config["MONGO_URI"] = "mongodb://localhost:50321/scrape_mars_app"

# Pass connection to the pymongo instance.
#client = pymongo.MongoClient(conn)

# Connect to a database.
#db = client.mars_db

@app.route('/')
def index():
    mars_results = mongo.db.mars_results.find_one()
    return render_template("index.html", mars_results=mars_results)

@app.route("/scrape")
def scrape():
    mars_results = mongo.db.mars_results  #or mars instead of mars_data
    mars_results = scrape_mars.scrape()
    mars_results.update(
            {},
            mars_results,
            upsert=True
    )
    return redirect("http://localhost:50321/", code=302)

if __name__ == "__main__":
    app.run(debug=True)