# Copyright (c) 2022, Novacept and contributors
# For license information, please see license.txt

# import frappe
#from frappe.model.document import Document

#class InstagramSetting(Document):
#	pass
import time
import ast
import json
import requests
import frappe
from frappe.model.document import Document

class InstagramSetting(Document):
	def validate(self):
		global insta_id
		global app_id
		global app_secret
		global short_lived_access_token
		global permanent_access_token
		global fb_page_id
		insta_id = ''
		app_id = self.app_id
		app_secret = self.app_secret
		short_lived_access_token = self.short_lived_access_token
		permanent_access_token = ''
		fb_page_id = self.fb_page_id
		try:
			permanent_access_token = self.long_lived_access()
			insta_id = self.insta_acc()
		except:
			frappe.throw((f'Please check APP detail or access token'))
	def long_lived_access(self):
#               print(f'\n\n\n\n long  \n\n\n\n')

		url = f"https://graph.facebook.com/v2.10/oauth/access_token?grant_type=fb_exchange_token&client_id={app_id}&client_secret={app_secret}&fb_exchange_token={short_lived_access_token}"

		payload={}
		headers = {}

		response = requests.request("GET", url, headers=headers, data=payload)
		return ast.literal_eval(response.text)['access_token']

#	def fb_page_id(self):
#		url = f'https://graph.facebook.com/v14.0/me/accounts?access_token={permanent_access_token}'
#		response = requests.request("GET", url)
#		return (ast.literal_eval(response.text)['data'])[0]['id']

	def insta_acc(self):
#		page_id = self.fb_page_id
		url = f'https://graph.facebook.com/v14.0/{fb_page_id}?fields=instagram_business_account&access_token={permanent_access_token}'
		response = requests.request("GET", url)
                # return response
		return (ast.literal_eval(response.text))['instagram_business_account']['id']

	def after_insert(self):
		frappe.db.set_value('Instagram Setting', self.name ,'long_lived_access_token', permanent_access_token)
		frappe.db.set_value('Instagram Setting', self.name ,'insta_id', insta_id)
		frappe.db.commit()
		try:
			setting = frappe.get_doc('Instagram Setting',self.name)
			if setting.long_lived_access_token and setting.insta_id:
				frappe.msgprint(('Success'))
		except:
				frappe.throw((f'DB Error'))


	def upload_post(self, caption, acc , media,media_type):
		insta_page = frappe.get_doc('Instagram Setting',acc)
		url = 'https://graph.facebook.com/v10.0/{}/media'.format(insta_page.insta_id)
		if media_type == 'IMAGE':
			payload={
			'image_url':media,
			'caption': caption,
			'access_token':insta_page.long_lived_access_token
			}
		elif media_type == 'VIDEO':
			payload={
			'video_url':media,
			'media_type':media_type,
			'caption': caption,
			'access_token':insta_page.long_lived_access_token
			}
		r = requests.post(url, data = payload)
		return ast.literal_eval(r.text)['id']

	def post(self, caption, acc , media,media_type):
#		print('\n\nINSTA \n\n')
#		print(acc)
#		print('\n\n\n\n')
		insta_page = frappe.get_doc('Instagram Setting',acc)
		post_id = self.upload_post( caption, acc , media,media_type)
		time.sleep(30)
		url = 'https://graph.facebook.com/v10.0/{}/media_publish'.format(insta_page.insta_id)
		payload = {
			'creation_id':post_id,
			'access_token': insta_page.long_lived_access_token
			}
		r = requests.post(url, data = payload)

		print('\n\n\n\n\n')
		print(r.text)
		print('\n\n\n\n\n')
		return ast.literal_eval(r.text)['id']
