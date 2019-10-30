# Automated Notification Service in a federated Cloud Setup for de.NBI Cloud

## Starting the Automated Notification Service

### First configuration
You can either edit the config.py in the config directory or create your own (e.g. config-prodcution.py) and use its path as an argument when starting the service (see below: Using gunicorn or Using docker).\
First the default config/config.py is loaded and then some of these values will be overwritten by your own custom config.py, so do not worry about changing the default config.py when using your own config.py.

You can set the APPLICATION_ROOT. The application will access its sites under this prefix, i.e. https://host-site/{APPLICATION_ROOT}.\
The standard configuration is 'news'.

You can set CC_SITES. These are the websites the online status is checked for and displayed on the Frontpage. They follow a structure:
```javascript
CC_SITES = {'Location': 'https://cloud.location-site.de/',
            'Location 2': 'https://cloud.uni-somewhere.de/'}
```

You should set SECRET_KEY when deploying to production. Flask recommends the following method:
<pre>$ python -c 'import os; print(os.urandom(16))'</pre>
The standard configuration is 'dev'.

You should set DEBUG to false when deploying to production.

For more configuration options please visit [Flask](https://flask.palletsprojects.com/en/1.1.x/config/).

### Using built-in Flask (only for development!)
It is recommended to run this service in a virtual environment. You can check out how to set up a virtual environment [here](https://docs.python.org/3/library/venv.html).

Once you activated the virtual environment you can install all necassary libarys and frameworks with:

<pre>$ pip install -r requirements.txt</pre>

Afterwards you maybe need to deactivate and re-activate the virtual environment, for changes to take place.

You need to point out to flask, which application you wanna run:

<pre>$ export FLASK_APP=newsservice</pre>

The port is set to 5000 on default.
In order to change the port of the service you can use:

<pre>$ export FLASK_RUN_PORT=****</pre>

Finally to run the service use:

<pre>$ flask run</pre>

The terminal should display something similar to this:
<pre>
 * Serving Flask app "newsservice"
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
</pre>

The service is now up and running. You can visit the web page at http://localhost:5000/{APPLICATION_ROOT}.\
Note: The APPLICATION_ROOT prefix will not be shown in: * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit).

### Using Gunicorn
It is recommended to run this service in a virtual environment. You can check out how to set up a virtual environment [here](https://docs.python.org/3/library/venv.html).

Once you activated the virtual environment you can install all necassary libarys and frameworks with:

<pre>$ pip install -r requirements.txt</pre>

Afterwards you maybe need to deactivate and re-activate the virtual environment, for changes to take place.

Finally to run the service use:

<pre>$ gunicorn -b host:port "newsservice:create_app('path/to/custom-config.py')"</pre>
In development you can use host=0.0.0.0 and port=5000. If you do not want to use a custom-config.py just leave it blank.

The terminal should display something similar to this:
<pre>
 [1979-01-01 00:00:00 +0200] [20228] [INFO] Starting gunicorn 19.9.0
 [1979-01-01 00:00:00 +0200] [20228] [INFO] Listening at: http://0.0.0.0:5000 (20228)
 [1979-01-01 00:00:00 +0200] [20228] [INFO] Using worker: sync
 [1979-01-01 00:00:00 +0200] [20231] [INFO] Booting worker with pid: 20231
</pre>

The service is now up and running. You can visit the web page at http://host:port/{APPLICATION_ROOT}.\
Note: The APPLICATION_ROOT prefix will not be shown in: [1979-01-01 00:00:00 +0200] [20228] [INFO] Listening at: http://0.0.0.0:5000 (20228).

### Using docker-compose
First you need to install Docker, as instructed [here](https://docs.docker.com/install/).\
Next, if you are operating on a Linux machine you also need to install docker-compose as instructed [here](https://docs.docker.com/compose/install/).

To run the service with default settings just use:
<pre>$ docker-compose up --build</pre>
The --build argument can be omitted if you already build the image and made no changes to the code.

To run the service with a custom config.py you have to change the docker-compose.yml like follows:\
<pre>
version: '3.5'
services:
  news-service:
    build:
       context: .
       dockerfile: Dockerfile
    volumes:
          - /path/to/your/name-of-config.py:/app/config/same-or-other-name-of-config.py
    command: gunicorn -b 0.0.0.0:5000 "newsservice:create_app('/app/config/same-or-other-name-of-config.py')"</pre>

### Publishing a News at the Automated Notification Service

If you are an Administrator at one of de.NBI Clouds facilities you can publish a News to the Service via an Application like cURL or Postman.

You can publish a News by posting a JSON-Document at the REST-Interface /savenews. 
The JSON-Document containing the News has the following structure:

```javascript
{"news" : {
	"title": "Title",
	"author": "Author",
	"text": "Text of the News",
	"tag": "Tag",
	"facility-ids": "FacilityID1,FacilityID2,...",
	"perun-login-token": "PERUN Log In Token"
	}
}
```
As every field is requested, omitting a field will throw an Error.

Each string has a max length defined by the database, so make sure your inputs match the following requierments:

| object  	 | max. length|
| ---------------|:----------:|
| title     	 | 200		|
| author   	 | 100    	|
| time 		 | 100    	|
| text   	 | 1500	 	|
| tag     	 | 50     	|
| facility id's  | 2000   	|



An example cURL call could look like this:
<pre> $ curl -X POST -H "Content-Type: application/json" -d  @/path/to/your/news.json http://localhost:5000/news/savenews </pre>

An example news.json could look like this:

```javascript
{"news" : {
	"title": "Update Analyze Service",
	"author": "John Doe",
	"text": "The Update v1.4 was deployed.",
	"tag": "Update",
	"facility-ids": "123,124",
	"perun-login-token": "edAf6FK8wIGkBn1u8hE_9zVK4_oOTCeMd8axTpA"
	}
}
```

After publishing a News it will be displayed at your [web page](http://localhost:5000/news)

### Requesting news of the Automated Notification Service with filters

In order to get already published News of the Automated Notification Service you can post a JSON-Document containing filters to the REST-Interface /requestnews via an Application like cURL or Postman.
The Automated Notification Service will return a JSON-Document containing News according to the filters you posted

The JSON-Document can contain the following filters:

```javascript
{
    "id": "",
    "tag": "",
    "author": "",
    "title": "",
    "text": "",
    "older": "",
    "newer": "",
    "facilityid":""
}
```
Fields can be omitted, and the values can be empty strings.

An example cURL call could look like this:
<pre> $ curl -X POST -H "Content-Type: application/json" -d  @/path/to/your/filter.json http://localhost:5000/news/requestnews </pre>

An example filter.json could look like this:

```javascript
{
    "id": "",
    "tag": "Update",
    "author": "John Doe",
    "older": "2019-07-21 17:00:00"
}
```
empty filters are going to be ignored during the filtering

### Requesting the MOTD of the Automated Notification Service

In order to request the MOTD, that is the last published News to the Automated Notification Service, you simply need to send a GET Request at /latestnews.
The Automated Notification Service returns a JSON-Document in the following format:
```javascript
{"title": "Title of latest news", 
 "text": "Text of latest news", 
 "author": "Author of latest news", 
 "time": "Time of latest news"}
```

An example cURL call could look like this:
<pre> curl -s 'http://127.0.0.1:5000/news/latestnews' </pre>

Also you can request the latest news in an already formatted-string by sending a GET Request at /latestnews-string..

### Implement the Custom Message of the Day at your Ubuntu/Debian Distribution

The Automated Notification Service contains custom de.NBI MOTD shell-scripts. In order to install them you need to copy the [scripts](https://github.com/prichter327/newsservice/tree/master/motdscripts) into the following directory of your Ubuntu/Debian system:
<pre>/etc/update-motd.d</pre>
You need Root-Permission to perfom this action. Via chmod make sure that the scripts are executable!
In order to display you may need to edit the **IP-ADRESS** and **PORT** inside the script *51-denbi-motd* in line 6:
<pre>curl -s 'http://'IP-ADRESS':'PORT'/latestnews'</pre>
In case you want to keep a slim log-in experience it is recommended to remove the scripts *10-help-text* and *50-motd-news* of the directory.

