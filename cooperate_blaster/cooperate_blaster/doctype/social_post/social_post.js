// Copyright (c) 2022, Novacept and contributors
// For license information, please see license.txt

//frappe.ui.form.on('Social Post', {
	// refresh: function(frm) {

	// }
//});
frappe.ui.form.on('Social Post', {
	validate: function(frm) {
			if (frm.doc.facebook === 0 && frm.doc.linkedin === 0 && frm.doc.instagram === 0) {
                        frappe.throw(__("Select atleast one Social Media Platform to Share on."));
                }
//                if (frm.doc.scheduled_time) {
  //                      let scheduled_time = new Date(frm.doc.scheduled_time);
    //                    let date_time = new Date();
      //                  if (scheduled_time.getTime() < (date_time.getTime() - 45*1000)) {
        //                        frappe.throw(__("Scheduled Time must be a future time."));
          //              }
            //    }
	},
	refresh: function(frm) {
//                frm.trigger('text');

                if (frm.doc.docstatus === 1) {
                        if (!['Posted', 'Deleted'].includes(frm.doc.post_status)) {
                                frm.trigger('add_post_btn');
                        }

//                        if (frm.doc.post_status !='Deleted') {
//                                let html='';
//                                if (frm.doc.twitter) {
//                                        let color = frm.doc.twitter_post_id ? "green" : "red";
//                                        let status = frm.doc.twitter_post_id ? "Posted" : "Not Posted";
//                                        html += `<div class="col-xs-6">
//                                                                <span class="indicator whitespace-nowrap ${color}"><span>Twitter : ${status} </span></span>
//                                                        </div>` ;
//                                }
//                                if (frm.doc.linkedin) {
//                                        let color = frm.doc.linkedin_post_id ? "green" : "red";
//                                        let status = frm.doc.linkedin_post_id ? "Posted" : "Not Posted";
//                                        html += `<div class="col-xs-6">
//                                                                <span class="indicator whitespace-nowrap ${color}"><span>LinkedIn : ${status} </span></span>
//                                                        </div>` ;
//                                }
//                                html = `<div class="row">${html}</div>`;
//                                frm.dashboard.set_headline_alert(html);
//                        }
                }
        },
	text: function(frm) {
		if (frm.doc.text) {
			frm.set_df_property('text', 'description', `Length ${frm.doc.text.length}`);
	//		frm.refresh_field('text');
	//		frm.trigger('validate_tweet_length');
		}
	},
	linkedin: function(frm) {
		frm.set_df_property('linkedin','description','(Only Image)');
	},

	linkedin_post: function(frm) {
		if (frm.doc.linkedin_post) {
			frm.set_df_property('linkedin_post', 'description', `Length ${frm.doc.linkedin_post.length}`);
//			frm.refresh_field('text');
//			frm.trigger('validate_tweet_length');
		}
	},
	caption: function(frm) {
		if (frm.doc.caption) {
			frm.set_df_property('caption', 'description', `Length ${frm.doc.caption.length}`);
//			frm.refresh_field('text');
//			frm.trigger('validate_tweet_length');
		}
	},
//	media_type: function(frm) {
//		if (frm.doc.media_type == 'IMAGE') {
//			frm.set_df_property('media_type', 'description','Only JPEG image of max 5 MB')
//		},
//		if (frm.doc.media_type == 'VIDEO') {
//			frm.set_df_property('media_type', 'description','Only MP4 viideo of max 30 MB and 30 sec')
//		},
//	},
        add_post_btn: function(frm) {
                frm.add_custom_button(__('Post Now'), function() {
                        frappe.call({
                                doc: frm.doc,
                                method: 'post',
                                freeze: true,
                                callback: function() {
                                        frm.reload_doc();
                                }
                        });
                });
        }
});
