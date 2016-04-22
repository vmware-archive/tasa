
Pivotal Topic and Sentiment Analysis Engine
============================================

This demo show cases Pivotal's Topic and Sentiment Analysis Engine using MADlib and GPText. The webserver will query a back-end (internal to Pivotal) corpus of over 800 million tweets in response to a search query and display topic & sentiment analysis dashboards powered by D3.js plots.

![TASA Animated GIF](https://github.com/pivotalsoftware/tasa/raw/gh-pages/images/tasacf_animated_highres.gif)

Pre-requisites
===============

This demo is not self-contained. There is a webserver component and there is a backend Greenplum Database Component.
This repo only contains the webserver component. To be able to get a fully functional demo, you'll have to build the back-end database, install the libraries (MADlib, GPText) and load a dataset as well. Please contact the author if you interested in going through all that.

We recommend that you install `Anaconda Python` for building this demo. Additionally, you will also need to install the `psycopg2` library (run: `conda install psycopg2` in your Anaconda environment). You should also be able to connect to the Pivotal GPDB DCA, which you to be within Pivotal PA VPN.

Configuration
==============

You'll have to create a config file to connect to your backend database. Create a file in your home directory `~/.dbconn.config` like so:
            
    [db_connection]
    user = gpadmin
    password = XXXXX
    hostname = 127.0.0.1 (or the IP of your DB server)
    port = 5432 (the port# of your DB)
    database = vatsandb (or the database you wish to connect to)

Starting the webserver
=======================

You can start the development server by running the script $TASA_HOME/tasa/deploy.This will start the dev server on localhost on port `8081`.

Front-end code
===============

Note that Ruby 2.1.1 and Bundler is required to develop and to compile the assets. A tool such as
`https://rvm.io/` may be useful. RVM installs both Ruby and Bundler. You may need to install RVM and bundler like so:

    \curl -sSL https://get.rvm.io | bash -s stable --ruby
    gem install bundler
    rvm install ruby-2.1.1

Additionally you'll also need to install phantomjs for your browser (Chrome). Checkout `https://bitbucket.org/ariya/phantomjs/downloads/`.Start the Rails development server:

    cd tasa/tasa
    bundle install
    bin/rails server

The Rails server serves the development assets at: `http://localhost:3000`. Before deploying, compile the UI assets via:

    cd tasa
    rake (only needed if you'd like to run all the tests, else go to step below)
    RAILS_ENV=production rake compile

If rake fails complaining that the folder webserver/common/static/tasa does not exist, create it and re-run rake.
Start the a development server:

    ./deploy

Adding a New Visualization
==========================

We have an example of how to add a time series graph in the `new-visualization-example` branch.

    git branch -a
    git checkout new-visualization-example

See the most recent commit on that branch for the example code.

PCF Deployment
===============

If you've followed the steps above to compile the new UI assets, you can deploy your app to PCF.
You'll first have to connect to your PCF endpoint, for example:

    cf login -a https://api.pcf1-rdu.nasa.pivotal.io

Enter your email address, password and choose the right space to deploy your app on (ex: "demos").

The file manifest.yml defined the buildpacks and other params relevant for a cf push.
The app can be pushed to your PCF instance using the following command:

    cf push tasacf -f manifest.yml

User Provided Service
======================

Create user provided service for database creds:

    cf cups tasacreds -p '{"hostname":"<hostname>","username":"<user>","password":"<password>", "databasename":"<database>", "port":"<port>" }'

Bind the service to the app using:

    cf bind-service tasacf tasacreds

Accessing the demo
===================

Currently the demo is accessible at: [https://tasacf.pcf1-rdu.nasa.pivotal.io/](https://tasacf.pcf1-rdu.nasa.pivotal.io/)

Author
=======

    Srivatsan Ramanujam, Apr-Aug 2013

Contributors
=============

    Ofri Afek (Design)
    Vinson Chuong (Dev)
    Greg Cobb (Dev) 
    Joelle Gernez (PM)
    Jarrod Vawdrey (DS)
