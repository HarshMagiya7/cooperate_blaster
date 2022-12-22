# Copyright (c) 2022, Novacept and contributors
# For license information, please see license.txt

# import frappe
#from frappe.model.document import Document
#import cv2
#class SocialPost(Document):
#	pass
from frappe.utils.file_manager import get_file_path
import datetime
import re
import os
import cv2
import frappe
from frappe import _
from frappe.model.document import Document

class SocialPost(Document):
	def validate(self):
		if not self.facebook and not self.instagram and not self.linkedin :
			frappe.throw(_("Select atleast one Social Media Platform"))

		if self.scheduled_time:
			current_time = frappe.utils.now_datetime() - datetime.timedelta(seconds = 45)
			scheduled_time = frappe.utils.get_datetime(self.scheduled_time)
			if scheduled_time < current_time:
				frappe.throw(_("Scheduled Time must be a future time"))
		if self.linkedin and self.media_type == 'VIDEO':
			frappe.throw(_('On LinkedIn only image media type is allowed'))

		if self.media_type:
			self.media_name_checker(self.media)
			self.media_validation()
	def submit(self):
		if self.scheduled_time:
			self.post_status = "Scheduled"
		super(SocialPost, self).submit()

	def on_cancel(self):
		self.db_set("post_status", "Cancelled")


	def media_validation(self):

		media = get_file_path(self.media)
		print(media)
		print('name')
#		media = media[1:]

		channels = []
		if self.facebook :
#			fb_config = frappe.get_doc('Facebook Configuration')
			channels.append('Facebook Configuration')
		if self.instagram :
#			ig_config = frappe.get_doc('Instagram Configuration')
			channels.append('Instagram Configuration')

		if self.linkedin:
#			in_config = frappe.get_doc('Linkedin Comfigutayion')
			channels.append('Linkedin Configuration')


		for channel in channels:
			status = frappe.db.get_single_value(channel,'doc_status')
			if not status:
				frappe.throw(_(f'{channel} is not enabled by ADMIN'))


		if self.media_type =='IMAGE':
			width, height, size, format = self.get_image_properties(media)
			self.image_validator(width, height, size, format, channels)
		elif self.media_type == 'VIDEO':
			width, height, size, format, duration = self.get_video_properties(media)
			self.video_validator(width, height, size, format, duration, channels)

	def media_name_checker(self,media):
		if re.search(' ',media):
			frappe.throw((f'Media name should not have a space in between'))

	def get_image_properties(self,img):
		format = self.file_type(img)
		size = self.file_size(img)
		width , height = self.img_dimension(img)
		return width , height , size , format
	def get_video_properties(self,vid):
		format = self.file_type(vid)
		size = self.file_size(vid)
		width, height, duration = self.vid_dim_and_dur(vid)
		return width, height, size, format, duration
	def image_validator(self, w, h, size, format, channels):

		for channel in channels:
			if format not in frappe.db.get_single_value(channel,'img_format').split(','):
				frappe.throw((f"Only {frappe.db.get_single_value(channel,'img_format')} is allowed on {channel.split(' ')[0]}"))
			if size > frappe.db.get_single_value(channel,'img_size'):
				print(size)
				print(frappe.db.get_single_value(channel,'img_size'))
				frappe.throw((f"Maximum {frappe.db.get_single_value(channel,'img_size')/1024}MB Image is allowed on {channel.split(' ')[0]}"))

	def video_validator(self, w, h, size, format, dur, channels):

		for channel in channels:
			if format not in frappe.db.get_single_value(channel,'vid_format').split(','):
				frappe.throw((f"Only {frappe.db.get_single_value(channel,'vid_format')} is allowed on {channel.split(' ')[0]}"))
			if size > frappe.db.get_single_value(channel,'vid_size'):
				frappe.throw((f"Maximum {frappe.db.get_single_value(channel,'vid_size')/1024}MB Video is allowed on {channel.split(' ')[0]}"))
			if dur < int(frappe.db.get_single_value(channel,'min_vid_dur')) or dur > int(frappe.db.get_single_value(channel,'max_vid_dur')):
				frappe.throw((f"Video length should be between {frappe.db.get_single_value(channel,'min_vid_dur')}s and {int(frappe.db.get_single_value(channel,'max_vid_dur'))/60}min only"))
	def file_size(self,file):
		file_status = os.stat(file)
		size = file_status.st_size
		return size

	def file_type(self,file):
		extension = os.path.splitext(file)[1]
		extension = extension.replace('.','').upper()
		return extension

	def img_dimension(self,img):
		cv2image = cv2.imread(img, flags=cv2.IMREAD_COLOR)
		height, width, channel  = cv2image.shape
		return width, height

	def vid_dim_and_dur(self,video):
		# Video frame dimensions
		vid = cv2.VideoCapture(video)
		height = vid.get(cv2.CAP_PROP_FRAME_HEIGHT)
		width = vid.get(cv2.CAP_PROP_FRAME_WIDTH)

		# Video duration
		frame_count = vid.get(cv2.CAP_PROP_FRAME_COUNT)
		fps = vid.get(cv2.CAP_PROP_FPS)
		duration = frame_count/fps

		return width , height , duration


	@frappe.whitelist()
	def post(self):
		try:
			if self.facebook:
				facebook = frappe.get_doc("Facebook Setting",self.page_name)
				if self.media_type:
					media_url = frappe.utils.get_url() + self.media
					print(f'\n\n\n\n{media_url}\n\n\n')
					facebook_post = facebook.post(self.text,self.page_name ,self.media_type ,media_url,self.fb_link,self.whatsapp_button, self.whatsapp_button_label)
				else:
#					facebook_post = facebook.post(self.text,self.page_name ,self.fb_link)
					facebook_post = facebook.post(self.text,self.page_name,self.media_type,self.media ,self.fb_link,self.whatsapp_button, self.whatsapp_button_label)
			if self.instagram:
				media_url = frappe.utils.get_url() + self.media
				instagram = frappe.get_doc("Instagram Setting",self.acc_name)
				instagram_post = instagram.post(self.caption,self.acc_name, media_url,self.media_type)
			if self.linkedin:
				linkedin = frappe.get_doc("LinkedIn Setting",self.link_page_name)
				linkedin_post = linkedin.post(self.linkedin_post, self.title, self.media)
				print(f'\n\n\n\n{linkedin_post}\n\n\n\n')
			self.db_set("post_status", "Posted")

		except Exception as e:
			frappe.throw(_(e))
			self.db_set("post_status", "Error")
			self.log_error("Social posting failed")

def process_scheduled_social_media_posts():
	print('\n\n\n\n\n\n\n PROCESS \n\n\n\n\n\n')
	posts = frappe.get_list(
		"Social Post",
		filters={"post_status": "Scheduled", "docstatus": 1},
		fields=["name", "scheduled_time"],
	)
	start = frappe.utils.now_datetime() - datetime.timedelta(minutes=4)
	end = frappe.utils.now_datetime() + datetime.timedelta(minutes=6)
	for post in posts:
		if post.scheduled_time:
			post_time = frappe.utils.get_datetime(post.scheduled_time)
			if post_time > start and post_time <= end:
				sm_post = frappe.get_doc("Social Post", post.name)
				sm_post.post()
