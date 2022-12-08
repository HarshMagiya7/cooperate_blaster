# Copyright (c) 2022, Novacept and contributors
# For license information, please see license.txt

# import frappe
#from frappe.model.document import Document

#class LinkedInSetting(Document):
#	pass
import frappe
import requests
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url_to_form
from frappe.utils.file_manager import get_file_path
from six.moves.urllib.parse import urlencode

class LinkedInSetting(Document):
	@frappe.whitelist()
	def validate(self):
		self.get_member_profile()
#		frappe.db.commit()
	def get_member_profile(self):
		response = requests.get(url="https://api.linkedin.com/v2/me", headers=self.get_headers())
		response = frappe.parse_json(response.content.decode())
		print(response)

		self.person_urn = response["id"]
		self.account_name= response["vanityName"]
		self.session_status= "Active"
		frappe.db.commit()

		print(f'\n\n\n\n{self.account_name}\n\n\n\n')
#		frappe.local.response["type"] = "redirect"
#		frappe.local.response["location"] = get_url_to_form("LinkedIn Settings", "LinkedIn Settings")

	def post(self, text, title, media=None):
		if not media:
			return self.post_text(text, title)
		else:
			media_id = self.upload_image(media)

			if media_id:
				return self.post_text(text, title, media_id=media_id)
			else:
				frappe.log_error("Failed to upload media.", "LinkedIn Upload Error")

	def upload_image(self, media):
		media = get_file_path(media)
		register_url = "https://api.linkedin.com/v2/assets?action=registerUpload"
		body = {
			"registerUploadRequest": {
				"recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
				"owner": "urn:li:organization:{0}".format(self.company_id),
				"serviceRelationships": [
					{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}
				],
			}
		}
		headers = self.get_headers()
		response = self.http_post(url=register_url, body=body, headers=headers)

		if response.status_code == 200:
			response = response.json()
			asset = response["value"]["asset"]
			upload_url = response["value"]["uploadMechanism"][
				"com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
			]["uploadUrl"]
			headers["Content-Type"] = "image/jpeg"
			response = self.http_post(upload_url, headers=headers, data=open(media, "rb"))
			if response.status_code < 200 and response.status_code > 299:
				frappe.throw(
					_("Error While Uploading Image"),
					title="{0} {1}".format(response.status_code, response.reason),
				)
				return None
			return asset

		return None

	def post_text(self, text, title, media_id=None):
		url = "https://api.linkedin.com/v2/shares"
		headers = self.get_headers()
		headers["X-Restli-Protocol-Version"] = "2.0.0"
		headers["Content-Type"] = "application/json; charset=UTF-8"

		body = {
			"distribution": {"linkedInDistributionTarget": {}},
			"owner": "urn:li:organization:{0}".format(self.company_id),
			"subject": title,
			"text": {"text": text},
		}

		reference_url = self.get_reference_url(text)
		if reference_url:
			body["content"] = {"contentEntities": [{"entityLocation": reference_url}]}

		if media_id:
			body["content"] = {"contentEntities": [{"entity": media_id}], "shareMediaCategory": "IMAGE"}

		response = self.http_post(url=url, headers=headers, body=body)
		return response

	def http_post(self, url, headers=None, body=None, data=None):
		try:
			response = requests.post(url=url, json=body, data=data, headers=headers)
			if response.status_code not in [201, 200]:
				raise

		except Exception as e:
			self.api_error(response)

		return response

	def get_headers(self):
		return {"Authorization": "Bearer {}".format(self.access_token)}

	def get_reference_url(self, text):
		import re

		regex_url = r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
		urls = re.findall(regex_url, text)
		if urls:
			return urls[0]

	def delete_post(self, post_id):
		try:
			response = requests.delete(
				url="https://api.linkedin.com/v2/shares/urn:li:share:{0}".format(post_id),
				headers=self.get_headers(),
			)
			if response.status_code != 200:
				raise
		except Exception:
			self.api_error(response)

	def get_post(self, post_id):
		url = "https://api.linkedin.com/v2/organizationalEntityShareStatistics?q=organizationalEntity&organizationalEntity=urn:li:organization:{0}&shares[0]=urn:li:share:{1}".format(
			self.company_id, post_id
		)

		try:
			response = requests.get(url=url, headers=self.get_headers())
			if response.status_code != 200:
				raise

		except Exception:
			self.api_error(response)

		response = frappe.parse_json(response.content.decode())
		if len(response.elements):
			return response.elements[0]

		return None

	def api_error(self, response):
		content = frappe.parse_json(response.content.decode())

		if response.status_code == 401:
			self.db_set("session_status", "Expired")
			frappe.db.commit()
			frappe.throw(content["message"], title=_("LinkedIn Error - Unauthorized"))
		elif response.status_code == 403:
			frappe.msgprint(_("You didn't have permission to access this API"))
			frappe.throw(content["message"], title=_("LinkedIn Error - Access Denied"))
		else:
			frappe.throw(response.reason, title=response.status_code)
