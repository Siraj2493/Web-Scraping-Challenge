Learn more or give us feedback
from flask import Flask, render_template
from scrape_mars import scrape
import pymongo

# Create an instance of our Flask app.
app = Flask(__name__)


# Set route
@app.route('/')
def index():
    #setup the database connection
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.mars_db
    # Store the entire team collection in a list
    mars = db.mars.find_one()
    client.close()
    #for key in mars:
    #    print(key)
    print(mars)

    # Return the template with the teams list passed in
    return render_template('index.html', mars=mars)
    #return('Doodah')

@app.route('/scrape')
def scrape_page():
    scrape()
    #setup the database connection
    conn = 'mongodb://localhost:27017'
    client = pymongo.MongoClient(conn)
    db = client.mars_db
    # Store the entire team collection in a list
    mars = db.mars.find_one()
    client.close()

    return render_template('index.html', mars=mars)


if __name__ == "__main__":
    app.run(debug=True)