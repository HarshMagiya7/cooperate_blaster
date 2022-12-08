# Copyright (c) 2022, Novacept and contributors
# For license information, please see license.txt

# import frappe
#from frappe.model.document import Document

#class FacebookSetting(Document):
#	pass
import ast
import json
import requests
import frappe
from frappe.model.document import Document
import urllib.parse

class FacebookSetting(Document):
	def validate(self):
		global page_id
		global app_id
		global app_secret
		global short_lived_access_token
		global permanent_access_token
		page_id = self.page_id
		app_id = self.app_id
		app_secret = self.app_secret
		short_lived_access_token = self.short_lived_access_token
		permanent_access_token = ''
		try:
			#print(f'\n\n\n\n DONE START  \n\n\n\n')
			permanent_access_token = self.permanent_access()
#			frappe.db.set_value('Facebook Setting', self.name ,'long_lived_access_token', permanent_access_token)
#			frappe.db.commit()
#			setting = frappe.get_doc('Facebook Setting',self.name)

		except:
			frappe.throw((f'Error'))

	def permanent_access(self):
#		print(f'\n\n\n\n PER  \n\n\n\n')
		long_lived_access_token =self.long_lived_access()
		account_id = self.acc_id()
		url = f"https://graph.facebook.com/v2.10/{account_id}/accounts?access_token={long_lived_access_token}"
		payload={}
		headers = {}

		response = requests.request("GET", url, headers=headers, data=payload)
		for i in range(len(ast.literal_eval(response.text)['data'])):
			if (ast.literal_eval(response.text)['data'][i]['id']) == page_id:
				return ast.literal_eval(response.text)['data'][i]['access_token']
#		return (ast.literal_eval(response.text)['data'])[0]['access_token']

	def acc_id(self):
#		print(f'\n\n\n\n ACC  \n\n\n\n')
		long_lived_access_token = self.long_lived_access()
		url = f"https://graph.facebook.com/v2.10/me?access_token={long_lived_access_token}"
		payload={}
		headers = {}

		response = requests.request("GET", url, headers=headers, data=payload)
		return (ast.literal_eval(response.text)['id'])

	def long_lived_access(self):
#		print(f'\n\n\n\n long  \n\n\n\n')

		url = f"https://graph.facebook.com/v2.10/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={short_lived_access_token}"

		payload={}
		headers = {}

		response = requests.request("GET", url, headers=headers, data=payload)
		return ast.literal_eval(response.text)['access_token']

	def after_insert(self):
		frappe.db.set_value('Facebook Setting', self.name ,'long_lived_access_token', permanent_access_token)
		frappe.db.commit()
		setting = frappe.get_doc('Facebook Setting',self.name)
		if setting.long_lived_access_token:
			print(setting.long_lived_access_token)
			frappe.msgprint(('Success'))
	def post(self, text, page ,media_type='', media=None,link = None, whatsapp_button = 0,whatsapp_label= None):
		print('\n\n\n\n')
#		facebook.post(self.text,self.page_name , self.title,self.media_type ,media_url,self.fb_link
#		print(page)
#		print('\n\n\n\n')
#		print(text)
		fb_page = frappe.get_doc('Facebook Setting',page)
		if not media:
			print('no media\n\n\n\n')
			print(fb_page.page_id)
			post_url = 'https://graph.facebook.com/{}/feed'.format(fb_page.page_id)
			print(post_url)
			payload = {
			'message': text,
			'access_token':fb_page.long_lived_access_token,
			'link':link
			}
			r = requests.post(post_url, data=payload)

		else:
			if whatsapp_button:
				url = 'https://graph.facebook.com/{}/feed'.format(fb_page.page_id)
				p1 = f"message={urllib.parse.quote(text,safe='')}"
				p2 = f"access_token={urllib.parse.quote(fb_page.long_lived_access_token,safe='')}"
				p3 = f"link={urllib.parse.quote(media,safe='')}"
				p4 = 'call_to_action=' + urllib.parse.quote('{"type": "WHATSAPP_MESSAGE","value":{"link_title":"'+whatsapp_label+'"}}',safe='')
				payload= f'{p1}&{p2}&{p3}&{p4}'
#				'message':text,
#				'access_token':fb_page.long_lived_access_token,
#				'link':media,
#				'call_to_action':{
#					'type': 'WHATSAPP_MESSAGE',
#					'value':{
#						'link_title':whatsapp_label
#						}
#					}
#				}
				print(payload)
				r = requests.request("POST", url, data=payload)
			else:
				if media_type == 'IMAGE':
					url = "https://graph.facebook.com/{}/photos".format(fb_page.page_id)
					payload={
					'url':media,
					'message': text,
					'access_token':fb_page.long_lived_access_token
					}
					r = requests.request("POST", url, data=payload)
				elif media_type == 'VIDEO':
					url = "https://graph-video.facebook.com/v14.0/{}/videos".format(fb_page.page_id)
					payload={
					'file_url':media,
					'description': text,
					'access_token':fb_page.long_lived_access_token
					}
					r = requests.request("POST", url, data=payload)
		print('\n\n\n\n\n')
		print(r.text)
		print('\n\n\n\n\n')
		return json.loads(r.text)['id']
