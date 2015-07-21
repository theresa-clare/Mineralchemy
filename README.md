#Mineralchemy

Designed for new and old rockhounds alike, Mineralchemy is a web application that expedites the search to collect minerals. The application aggregates listings from Etsy, eBay, and Minfind based on the user's search specifications, as well as filters those that are non-raw specimens (i.e. various types of jewelry). Users can be directed to the listing's original site to purchase the mineral by clicking on the listing's title. Users may also create an account to save their favorite listings in order to view the listing at a later time. Furthermore, Mineralchemy also doubles as an educational tool by constructing a full vizualization of the classification of minerals. This enables users to discover and learn more about new minerals and those they may potentially be interested in.

##Technology Stack

**Frontend:** HTML, CSS, Javascript, jQuery, D3, Bootstrap, Jinja<br/>
**Backend:** Python, Flask, SQLite, BeautifulSoup<br/>
**APIs:** Etsy, eBay<br/>

![image](/static/images/mineralchemy-architecture.png)
![image](/static/images/homepage.png)

##Search for Minerals

Each search is composed of keywords (single or multi-worded string) and a price range (minimum and maximum amount). When the user clicks <kbd>Submit</kbd>, the input from the search form is passed through and used as the data for 3 separate AJAX calls. The calls go to their respective route on the server. The data is used as the arguments to the search functions of Etsy, eBay, and Minfind. 

Listings returned from the Etsy and eBay APIs and those scraped from Mindat using BeautifulSoup are parsed and put back together in a uniform format. Along with the number of listings found, this is returned as a JSON response to the AJAX call. Once received, the DOM is updated dynamically by adding elements using jQuery.

![image](/static/images/search.png)
![image](/static/images/search_results1.png)
![image](/static/images/search_results2.png)
![image](/static/images/search_results3.png)

##Favorite Minerals

To use this feature, users must create an account or sign in prior to searching. When the user clicks on <kbd>Favorite</kbd>, the details of the listing and the user's ID are added to the database. 

A user can view his or her favorite listings by visiting the profile page. The database is queried for all of the user's favorite listings, which are then displayed by origin.

![image](/static/images/login.png)
![image](/static/images/search_results4.png)

##Discover Minerals

Users can discover minerals by exploring radial tree visualizations of the Nickel-Strunz classification of minerals. Each primary group of the classification system is represented by 1 - 3 radial trees. Users interact with the visualizations by clicking on a node. This will direct the users to the mineral's specific details page on Mindat, the world's largest mineral database. 

The source, target, and URL data is stored in CSV files. The creation of nodes, links, and hierarchical associations from these files is completed via D3.

![image](/static/images/discover1.png)
![image](/static/images/discover2.png)

##Set up

Clone or flork this repo:

```
https://github.com/theresa-clare/Mineralchemy.git
```

Create and activate a virtual environment inside your project directory:

```
virtualenv env
source env/bin/activate
```

Install the requirements:

```
pip install -r requirements.txt
```

Get your own secret keys for [Etsy](http://developer.etsy.com) and [eBay](www.ebay.com). Save them to a file <kbd>secrets.txt</kbd>. Your file should look something like this:

```
YOUR_ETSY_KEY
YOUR_EBAY_KEY
```

Set up the database:

```
python -i model.py
db.create_all()
```

Run the app:

```
python server.py
```

Navigate to 'localhost:5000/' to search and discover minerals!

##Future Plans

Mineralchemy is the developer's first independent programming project. With only 4 weeks to complete this project, time was scarce to design, build, and optimize Mineralchemy. More features will be implemented in the near future (e.g. full Strunz mineral classification on the Discover page, searching the classification visualizations by a specific mineral, sorting listings by price, viewing all listings at once instead of separated by origin).