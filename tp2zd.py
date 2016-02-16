# coding=utf-8
import requests
import re
import time
import string
import json
import ConfigParser
import io

Config = ConfigParser.ConfigParser()
Config.read("tp2zd.ini")
domain = Config.get("Trustpilot", "domain")
tpapikey = Config.get("Trustpilot", "tpapikey")

zdhost = Config.get("Zendesk", "zdhost")
zduser = Config.get("Zendesk", "zduser")
zdpass = Config.get("Zendesk", "zdpass")

zdfldReviewID = Config.get("CustomFieldIDs", "zdfldReviewID")
zdfldReviewerID = Config.get("CustomFieldIDs", "zdfldReviewerID")

tpUrl = 'https://api.trustpilot.com/v1/business-units/find?name='+domain+'&apikey='+tpapikey
data = '{}'
response = requests.get(tpUrl, data=data)
bizUnitJson = response.json()
bizUnitID = bizUnitJson['id']

while True:

	tpUrl = 'https://api.trustpilot.com/v1/business-units/'+bizUnitID+'/reviews?apikey='+tpapikey+'&responded=false&includeReportedReviews=false&perPage=30'
	data = '{}'
	response = requests.get(tpUrl, data=data)
	reviews_data = response.json()
	print 'Fetch from Trustpilot: ' + str(response)

	for review in reviews_data['reviews']:
		review_text = review['text'].replace('"', r'\"')
		review_subject = review['title'].replace('"', r'\"')
		review_id = review['id']
		review_stars = review['stars']
		reviewer_id = review['consumer']['id']
		reviewer_name = review['consumer']['displayName'].replace('"', r'\"')

# Test check if a ticket exists with reviewID before
		queryResponse = requests.get('https://'+zdhost+'.zendesk.com/api/v2/search.json?query=fieldvalue:'+review_id, auth=(zduser, zdpass))
		queryRespJson = queryResponse.json()
		queryTicketCount = queryRespJson['count']

		if  queryTicketCount == 0:
			print 'Importing Review with id= '+review_id
		else:
			print 'Review with id = '+review_id+' already imported'
		
		zd_ticket_body_trim = 'You received a new '+ str(review_stars) +' star review at ' + 'https://www.trustpilot.com/review/'+domain+'/' + review_id
		zd_ticket_body = zd_ticket_body_trim +'       '+review_text
		
		if  queryTicketCount == 0 and (review_stars <4 or len(review_text) > 49):
# Now Post the fresh ticket
			url = 'https://'+zdhost+'.zendesk.com/api/v2/tickets.json'

			try:
			
				data = '{"ticket":{"requester": {"name": "'+reviewer_name+'", "email": "'+review_id+'@no-reply.com"}, "subject": "Review: '+ review_subject +'", "comment": { "body": "'+ zd_ticket_body +'" },"fields": { "'+zdfldReviewID+'":"'+review_id+'", "'+zdfldReviewerID+'":"'+reviewer_id+'" }}}'
				response = requests.post(url, data=data, headers={"Content-Type":"application/json"}, files={}, cookies=None, auth=(zduser, zdpass))
				if response.status_code == 422:
					data2 = '{"ticket":{"requester": {"name": "'+reviewer_name+'", "email": "'+review_id+'@no-reply.com"}, "subject": "Review: '+ review_subject +'", "comment": { "body": "'+ zd_ticket_body_trim +'" },"fields": { "'+zdfldReviewID+'":"'+review_id+'", "'+zdfldReviewerID+'":"'+reviewer_id+'" }}}'
					#print data2
					response2 = requests.post(url, data=data2, headers={"Content-Type":"application/json"}, files={}, cookies=None, auth=(zduser, zdpass))
					
			except UnicodeEncodeError:
				data3 = '{"ticket":{"requester": {"name": "Unknown", "email": "'+review_id+'@no-reply.com"}, "subject": "Review: Unknown", "comment": { "body": "'+ zd_ticket_body_trim +'" },"fields": { "'+zdfldReviewID+'":"'+review_id+'", "'+zdfldReviewerID+'":"'+reviewer_id+'" }}}'
				#print data3
				response3 = requests.post(url, data=data3, headers={"Content-Type":"application/json"}, files={}, cookies=None, auth=(zduser, zdpass))
				if response3.status_code == 422:
					print '*********************** ERRRRR IMPORTING: ' + review_id				
	
	time.sleep(60)


