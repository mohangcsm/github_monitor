This project is aimed to identify if there is a new public repository added into any given github organization

The following are the dependency libraries. User PIP or EASY_INSTALL or BREW to install the below.

	requests
	json
	pymongo
	
Make sure "Mongo" running with following values:

	MONGO_HOST = '127.0.0.1'
	MONGO_PORT = 27017
	MONGO_USERNAME = ''
	MONGO_PASSWORD = ''

Running Program : 
	> python github_monitor.py <org_name> <auth_token>