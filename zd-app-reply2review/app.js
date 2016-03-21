(function () {

    return {

        events: {
            'app.activated': 'doSomething',
            'ticket.save': 'replyReview',
            'getToken.done': 'tokenSuccess',
            'getToken.fail': 'tokenFail'
        },

        requests: {

            getToken: function (new_task_data) {
                return {
                    url: 'https://api.trustpilot.com/v1/oauth/oauth-business-users-for-applications/accesstoken',
                    headers: {"Authorization": "Basic [Base64 of APIKey:Secret]"},
                    type: 'POST',
                    contentType: 'application/x-www-form-urlencoded',
                    data: {'grant_type': 'password', 'username': this.setting('tpuser'), 'password': this.setting('tppass')}
                };
            },

            tpReplyToReview: function (reviewID, token, replyText) {
                console.log("TP Review Reply Call going with reviewID= " + reviewID + " token=" + token + " Reply Text:" + replyText);
                return {
                    url: 'https://api.trustpilot.com/v1/private/reviews/' + reviewID + '/reply?token=' + token,
                    type: 'POST',
                    contentType: 'application/json',
                    data: JSON.stringify({
                        "message": replyText
                    }),
                    secure: true

                };
            }

        },

        tokenSuccess: function (data) {
            console.log("token success ");
            console.log(data.access_token);
            //access_token = data.access_token;
            var ticket = this.ticket();
            ticket.customField("custom_field_29760098",data.access_token); // access token
            // this.ticket's 29760098
            services.notify('Ready to Post Review Replies from Zendesk');
        },

        tokenFail: function (data) {
            console.log("token success ");
            console.log(data);
            services.notify('ERROR GETTING OAUTH TOKEN: CANNOT Post Review Replies from Zendesk');
        },

        doSomething: function () {
            console.log("Reply to Review App is activated");
            this.ajax('getToken');
        },

        replyReview: function () {
            var ticket = this.ticket();
            console.log('starting to reply review to ' + ticket.customField("custom_field_28948647") + "with reply: " + this.comment().text().replace(/<br\s*\/?>/mg,"\n") + "token= "+ ticket.customField("custom_field_29760098"));
            //console.log(ticket.comments);
			return this.promise(function (done,fail) {
				this.ajax('tpReplyToReview', ticket.customField("custom_field_28948647"), ticket.customField("custom_field_29760098"), this.comment().text().replace(/<br\s*\/?>/mg,"\n")).then(
					function(data) {
						services.notify('Successfully replied review');
						done();
					},
					function() {
						console.log("Failed to reply");
						services.notify('Problem with the POSTing Reply to this Review', 'error');
						done();
					}
					);
			});
        }
    };

}());