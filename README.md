Pivotal Topic and Sentiment Analysis Engine
============================================

	This demo show cases Pivotal's Topic and Sentiment Analysis Engine using MADlib and GPText.
        The webserver will query a back-end (internal) corpus of over 47 million tweets in response
        to a search query and display topic & sentiment analysis dashboards powered by D3.js plots.

Author
=======

	Srivatsan Ramanujam <sramanujam@gopivotal.com>, Apr-Aug 2013

Pre-requisites
===============

	This demo is not self-contained. There is a webserver component and there is a back-end Greenplum Database Component.
        This repo only contains the webserver component.        
        To be able to get a fully functional demo, you'll have to build the back-end database, install the libraries (MADlib, GPText)
        and load a dataset as well. Please contact the author if you interested in going through all that.

        This following are the pre-requisites for the webserver component alone:

	1) Your python should have psycopg2.
	2) You should also have django installed on your machine.
	3) You should also be able to connect to the Analytics DCA (which means you should be within GP's LAN).
	4) Add the environment variable 'export DJANGO_SETTINGS_MODULE=webserver.settings' to your bashrc.
        5) Set the environment variable DATA_FOLDER in your ~/.bashrc to point to your MEDIA_ROOT for Django
                example: 
                        export DATA_FOLDER = /tmp/django_media_root

Installation
=============

	1) After unzipping the tarball or cloning to the git repository, run the following:
                cd $NLPDEMO_HOME/nlpdemo 
  		sudo python setup.py build
  		sudo python setup.py install

    2) You'll also have to create a config file to connect to your backend database.
       Create a file in your home directory : ~/.dbconn.config
       that should look like so (without the "______") :
            ____________________
            [db_connection]
            user = gpadmin
            password = XXXXX
            hostname = 127.0.0.1 (or the IP of your DB server)
            port = 5432 (the port# of your DB)
            database = vatsandb (the database you wish to connect to)
            ____________________


Starting the webserver
=======================

	You can start the development server by running the script $NLPDEMO_HOME/nlpdemo/start_dev_server.
        This will start the dev server on port:8081

        To run this on production, you'll have to setup nginx, download gunicorn and eventlet 
        and suitably modify $NLPDEMO_HOME/gunicorn.start.sample to work in your environment  

Accessing the demo on a browser
================================

        Once the demo server has been started, you can access the topic and sentiment analysis engine 
        through the following links:

        Topic Analysis Engine: http://<demo server ip>:8081/gp/topic/home
        Sentiment Analysis Engine: http://<demo server ip>:8081/gp/senti/home

Code Organization
==================

	All relevant Intellectual Property associated with this demo is under $NLPDEMO_HOME/nlpdemo/webserver
        There is a module for topic analysis and one for sentiment analysis.

New UI Code
===========

    Note that Ruby 2.1.1 and Bundler is required to develop and to compile the assets. A tool such as
    https://rvm.io/ may be useful. RVM installs both Ruby and Bundler.

    Start the Django server:
    ```bash
    cd nlpdemo
    ./start_dev_server
    ```

    Start the Rails development server:
    ```bash
    cd nlpdemo/tasa
    bundle install
    bin/rails server
    ```

    The Rails server serves the development assets at: http://localhost:3000

    Before deploying, compile the UI assets via:
    ```bash
    cd tasa
    RAILS_ENV=production rake compile
    ```
    We have a sample deployment script in `/nlpdemo/deploy`. Please refer to the comments inside.

Adding a New Visualization
==========================

    We have an example of how to add a time series graph in the `new-visualization-example` branch.

    ```bash
    git branch -a
    git checkout new-visualization-example
    ```

    See the most recent commit on that branch for the example code.

PCF Deployment
===============

All PCF related deployment code is in the branch pcfize
The file manifest.yml defined the buildpacks and other params relevant for a cf push.
The app can be pushed to your PCF instance using the following command:

```
cf push tasacf -f manifest.yml
```

User Provided Service
======================
Create user provided service for database creds:

```
cf cups tasacreds -p '{"hostname":"<hostname>","username":"<user>","password":"<password>", "databasename":"<database>", "port":"<port>" }'
```
Bind the service to the app using:

```
cf bind-service tasacf tasacreds
```

Accessing the demo
===================
Currently the demo is accessible at: http://tasacf.pcf1-sc.vchs.pivotal.io/tasa/index.html
