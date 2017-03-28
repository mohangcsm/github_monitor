import requests, os, json, sys
from pymongo import MongoClient

requests.packages.urllib3.disable_warnings()

# mongodb config
MONGO_HOST = '127.0.0.1'
MONGO_PORT = 27017
MONGO_USERNAME = ''
MONGO_PASSWORD = ''

client = MongoClient(MONGO_HOST,MONGO_PORT)
db=client.git_monitor			# db initialization

def banner():
	print '#################################################################'
	print '#		Program Name : Github Monitor Project	    	#'
	print '#		Author Name : Mohan Kallepalli			#'
	print '#		Version No : v1 				#'
	print '#################################################################'

# -------------------------------------
def find(id):
# -------------------------------------
	try:
		res = db.recods.find({'id':id}).count()
		if res != 0:
			return True
		else:
			return False
	except Exception as ae:
		return None

# -------------------------------------
def insert(ele):
# -------------------------------------
	try:
		res = db.recods.insert(ele)
		return res
	except Exception as ae:
		return 'error'

def download(org,repos_data,page,token):
	repos_url = 'https://api.github.com/orgs/'+org+'/repos?type=public&per_page=1000&page='+str(page)
	header = {
	'Authorization': 'token '+token,
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
	}
	data = requests.get(repos_url, headers=header, verify=False)
	name_data = json.loads(data.text)
	for names in name_data:
		repos_data.append(names)
	heads = data.headers
	links = heads['link'].split(',')

	for link in links:
		if "next" in link.lstrip():
			download(org,repos_data,page+1,token)
		else:
			break
	return repos_data

# -------------------------------------
def repos(org,token):
# -------------------------------------
	repos_data = []
	repos_data = download(org,repos_data,1,token)
	c=0
	public_repo = []
	for ele in repos_data:
		if not find(ele['id']):
			insert(ele)
			public_repo.append([ele['name'],ele['html_url']])
			c=c+1

	if c != 0:
		print "Total "+str(c)+" new public repo(s) found\n"
		c=0
		for repo_ in public_repo:
			c=c+1
			print str(c)+". "+repo_[0]+"\t\t"+repo_[1]
	else:
		print "No new public repos found"
		
# -------------------------------------
def orgs(org,token):
# -------------------------------------
	try:
		orgs_url = 'https://api.github.com/orgs/'+org
		header = {
		'Authorization': 'token '+token,
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
		}
		orgs_data = requests.get(orgs_url, headers=header, verify=False)
		orgs_data = json.loads(orgs_data.text)
		if 'Bad credentials' in orgs_data:
			exit("token invalid. check token once and try again")
		elif 'Not Found' in orgs_data:
			exit("org_name invalid. check once and try again")
		elif 'public_repos' in orgs_data:
			total_num = orgs_data['public_repos']
		else:
			exit("error in fetching repo information. check inputs once and try again")
			
		nos = db.toal_num.find().skip(db.toal_num.count() - 1)
		for no in nos:
			if no['tno'] != total_num:
				db.toal_num.insert({'tno':total_num})
				delta = total_num - no['tno']
				if delta > 0:
					repos(org,token)
			else:
				print "No change in total number of public repos"
	except Exception:
		exit("Error Occured. Try again")

# -------------------------------------
def main(argv):
# -------------------------------------
	try:
		if len(argv) != 2:
			print "Error. Try again"
			print "Usage : python github_monitor.py <org_name> <auth_token>"
			exit()
		else:
			banner()
			orgs(argv[0],argv[1])
	except KeyboardInterrupt:
		print " Identified. Program Terminated"
	except Exception as Ae:
		print "Program Terminated" + str(Ae)

# -------------------------------------
if __name__ == '__main__':
# -------------------------------------
    main(sys.argv[1:])




