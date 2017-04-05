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
	print '#		Version No : v2 				#'
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
	repos_url = 'https://api.github.com/orgs/'+org.title()+'/repos?type=public&per_page=1000&page='+str(page)
	header = {
	'Authorization': 'token '+token,
	'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
	}
	# proxies = {"https":"127.0.0.1:8080"},
	data = requests.get(repos_url,  headers=header, verify=False)
	name_data = json.loads(data.text)
	for names in name_data:
		# print names
		repos_data.append(names)
	heads = data.headers
	# print heads
	links = heads['link'].split(',') if 'link' in heads else []
	if links != []:
		for link in links:
			if "next" in link.lstrip():
				download(org,repos_data,page+1,token)
			else:
				break
	return repos_data

# -------------------------------------
def repos(org,token):
# -------------------------------------
	line_width = 50
	repos_data = []
	repos_data = download(org,repos_data,1,token)
	# print repos_data
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
			print str(c)+"\t"+repo_[0].ljust(line_width)+repo_[1]
	else:
		print "No new public repos found"
	
	print "\n\n"

# -------------------------------------
def orgs(org,token):
# -------------------------------------
	try:
		orgs_url = 'https://api.github.com/orgs/'+org.title()
		header = {
		'Authorization': 'token '+token,
		'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36'
		}
		# proxies = {"https":"127.0.0.1:8080"},
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
		
		skip_first = db.toal_num.count({'org':org.title()}) - 1

		if skip_first < 0:
			db.toal_num.insert({'tno':total_num,'org':org.title()})
			nos = db.toal_num.find({'org':org.title()})
			repos(org,token)
		else:
			nos = db.toal_num.find({'org':org.title()}).skip(skip_first)

		for no in nos:
			if no['tno'] != total_num:
				db.toal_num.insert({'tno':total_num,'org':org.title()})
				delta = total_num - no['tno']
				if delta > 0:
					repos(org,token)
			elif skip_first >= 0:
				print "No change in total number of public repos"

		ch = 'N'
		ch = raw_input("Do you want to see all public repos (y/N): ")
		if ch == 'y' or ch == 'Y':
			all_repos(org)

	except Exception as aaa:
		print str(aaa)
		exit("Error Occured. Try again")

def all_repos(org):
	c = 1
	line_width = 50
	
	records = db.toal_num.find({"org": org.title()})
	for record in records:
		total_count = record['tno']

	print "\nTotal Number of Public Repos: "+str(total_count)+"\n"
	print "Sno\t"+"Repo Name".ljust(line_width)+"Repo Url"
	print "***\t"+"*********".ljust(line_width)+"********\n"

	repos = db.recods.find()
	for repo in repos:
		if org.title() in repo['full_name'].title():
			print str(c)+"\t"+repo['full_name'].lstrip((org+"/")).ljust(line_width)+repo['html_url']
			c = c+1

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
