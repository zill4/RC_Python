'''
_______________LEGACY CODE FOR REFERENCE_______________
secret = ''
key = ''
url = "https://platform.ringcentral.com/restapi/oauth/token"
client_id = base64.b64encode(secret + ':' + key)
print(client_id)
payload = "grant_type=password&username=%&password=&extension="
headers = {
    'authorization': client_id,
    'accept': "application/json",
    'content-type': "application/x-www-form-urlencoded",
    'cache-control': "no-cache",
    }
print(headers['authorization'])
response = requests.request("POST", url, data=payload, headers=headers)
print(response.text)
________________________________________________________
'''
import numpy
import requests
import requests.auth
import threading
import time
import base64
import json
import sys

'''
________________AUTHORIZATION CREDENTIALS___________________
'''
#APP SECERET
secret = ''
#APP KEY
key = ''
#URL for token request. Use Sandbox URL for non-live applications.
url = "https://platform.ringcentral.com/restapi/oauth/token"
#Combine the key and secret to make a authorization key, must be in base64.
authorization = base64.b64encode(secret + ':' + key)
'''
_____________________________________________________________
'''

#Start() grabs a token and authorizes the account for API calls.
def start():
    #Create an Client_auth_key, let requests handle the nitty gritty. Similar to last step.
    client_auth = requests.auth.HTTPBasicAuth('', '')
    #Data required to access the API, basically your login information.
    post_data = {"grant_type": "password", "username": "phonenumber", "password": "", "extension":""}
    #Headers are necessary for authorizing this transaction. The request will
    headers = {"authorization": authorization,
            "accept": "application/json",
            "content-type": "application/x-www-form-urlencoded",
            "cache-control": "no-cache"}
    response = requests.post("https://platform.ringcentral.com/restapi/oauth/token", auth=client_auth, data=post_data, headers=headers)
    #save token information.
    token = response.json()
    return token
#Start returns the token.
token = start()
#saving the access token when needed.
access_token = token['access_token']
#bearer token needed for most API headers saved in the correct Bearer %s format.
bearer_token = "Bearer %s" %(access_token)


#Calls getGroup: the list of groups attached to my account.
def get_group_list():
    url = "https://platform.ringcentral.com/restapi/v1.0/glip/groups"
    headers = {
    'content-type': "application/json",
    'accept': "application/json",
    'authorization': bearer_token,
    'cache-control': "no-cache",
    }
    response = requests.get(url, headers = headers)
    print(response)
    if(response.status_code == 429):
        api_wait()
        get_posts(id)
    return response
group_list = get_group_list()
gList = group_list.json()


#calls getPerson: requires an ID parameter
def get_person(id):
    url = "https://platform.ringcentral.com/restapi/v1.0/glip/persons/"
    url_id = "https://platform.ringcentral.com/restapi/v1.0/glip/persons/ %s"%(id)
    headers = {
        'content-type': "application/json",
        'accept': "application/json",
        'authorization': bearer_token,
        'cache-control': "no-cache",
    }
    response = requests.get(url_id, headers=headers)
    print(response)
    if(response.status_code == 429):
        api_wait()
        get_posts(id)
    return response


def get_posts(id):
    url = "https://platform.ringcentral.com/restapi/v1.0/glip/posts"
    querystring = {"groupId": id, "recordCount":"250"}
    headers = {
        'content-type': "application/json",
        'accept': "application/json",
        'authorization': bearer_token,
        'cache-control': "no-cache",
    }
    response = requests.get(url, headers=headers, params = querystring)
    #must catch bad api responses
    print(response)
    if(response.status_code == 429):
        api_wait()
        get_posts(id)
    r = response.json()
    return r


def get_page(id, p_id):
    url = "https://platform.ringcentral.com/restapi/v1.0/glip/posts"
    querystring = {"groupId": id,"pageToken": p_id, "recordCount":"250"}
    headers = {
        'content-type': "application/json",
        'accept': "application/json",
        'authorization': bearer_token,
        'cache-control': "no-cache",
    }
    response = requests.get(url, headers=headers, params = querystring)
    print(response)
    if(response.status_code == 429):
        api_wait()
        get_posts(id)
    r = response.json()
    return r


def collect_people_names():
    #people = numpy.zeros(shape=(100,1000))
    r, m = 100, 500
    Matrix = [[0 for x in range(m)] for y in range(r)]
    out_count = 0
    in_count = 0
    for recs in gList['records']:
        people = gList['records'][out_count]['members']
        print(out_count)
        in_count = 0
        for mems in recs['members']:
            print(in_count)
            Matrix[out_count][in_count] = mems
            in_count = in_count + 1
        out_count = out_count + 1
    return Matrix
people = collect_people()


def id_people():
    file = open("collected_people.tsv","w")
    file.write("firstName\tlastName\n")
    api_call_count = 0
    bad_token_count = 0
    print("Starting data collection for User ID's")
    print("This will take awhile...")
    for i in xrange(60,0,-1):
        time.sleep(1)
        sys.stdout.write(str(i)+' ')
        sys.stdout.flush()
    for x in people:
        for y in x:
            if y is not 0:
                try:
                    if api_call_count is not 29:
                        person = get_person(y)
                        person = person.json()
                        file.write(person['firstName'])
                        print(person['firstName'])
                        file.write("\t")
                        file.write(person['lastName'])
                        print(person['lastName'])
                        file.write("\t")
                        file.write(y)
                        file.write("\n")
                        api_call_count = api_call_count + 1
                        print (api_call_count)
                    else:
                        api_wait()
                        api_call_count = 0
                except Exception as ex:
                    print("error reached: %s" %(ex))
                    bad_token_count = bad_token_count + 1
                    api_wait()
                    if bad_token_count is 10:
                        start()
                        bad_token_count = 0
    file.close()
    return person


def api_wait():
        print("API call limit reached waiting 1 minute.")
        for i in xrange(60,0,-1):
            time.sleep(1)
            sys.stdout.write(str(i)+' ')
            sys.stdout.flush()


def write_message(id):
    try:
        rj = get_posts(id)
        for x in rj['records']:
            file.write(x['text'])
            file.write('\n')
            #print(x['text'])
            for x in rj['navigation']:
                paging = True if "prevPageToken" in x else False
                if(paging):
                    write_next_page(id, rj['navigation']['prevPageToken'])
    except Exception as ex:
        print("error reached: \"%s\"" %(ex))


def write_next_page(id, p_id):
    try:
        rj = get_page(id, p_id)
        for x in rj['records']:
            file.write(x['id'])
            file.write('\t')
            file.write(x['text'])
            file.write('\n')
            for x in rj['navigation']:
                paging = True if "prevPageToken" in x else False
                if(paging):
                    write_next_page(id, rj['navigation']['prevPageToken'])
    except Exception as ex:
        print("error reached: \"%s\"" %(ex))


def collect_records():
    file = open('messages_collect.csv', 'w')
    for x in gList['records']:
        write_message(x['id'])
    file.close()
