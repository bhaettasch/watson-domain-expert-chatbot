/**
 * SurfaceBeam Web Presentation Module
 *
 * @author Benjamin Haettasch
 * @version 0.1
 */

/// <reference path="../bwb.ts" />
/// <reference path="../../ext/jquery.d.ts" />
/// <reference path="json_answers.ts" />

module bwb
{
    import WatsonMessage = bwb.WatsonMessage;
    export class APIConnector
    {
        lastLoadedMessageID : number;
        lastLoadedWatsonMessageID : number;

        messageLoadingInterval : number;
        fastReload : boolean;
        
        /**
         * Constructor
         *
         * @param apiRoot URL pointing to API root
         * @param chatID ID of the current chat
         */
        constructor(private apiRoot : string, private chatID : number) {
            this.lastLoadedMessageID = -1;
            this.lastLoadedWatsonMessageID = 0;
            this.fastReload = false;

            $.ajaxSetup(<JQueryAjaxSettings>{
                beforeSend: function(xhr, settings) {
                    if (!APIConnector.csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", BWB.getInstance().csrfToken);
                    }
                }
            });
        }

        /**
         * Start API connector
         */
        public start() : void
        {
            this.startMessageLoadingInterval();
        }

        /**
         * Load messages in a regular interval
         */
        private startMessageLoadingInterval(reloadNow: boolean = true) : void
        {
            if(this.messageLoadingInterval != 0)
                window.clearInterval(this.messageLoadingInterval);
            if(reloadNow)
                this.loadMessages();
            this.messageLoadingInterval = window.setInterval(() => {this.loadMessages()}, this.fastReload ? 500 : 2000);
        }

        /**
         * Change between lazy and aggressive reloading strategy
         *
         * @param fast fast reloading?
         * @param reloadNow Also do a load request now?
         */
        private activateFastReloading(fast : boolean, reloadNow : boolean = false) : void {
            if(this.fastReload != fast)
            {
                this.fastReload = fast;
                this.startMessageLoadingInterval(reloadNow);
            }
        }

        /**
         * Post a new message to the chat
         */
        public sendMessage(message: string) : void
        {
            $.post(
                this.apiRoot+'chat/messages/add/',
                {
                    'text':message,
                    'chat':this.chatID
                },
                (answer: JSONAnswer_Status) => {
                    if(answer.status != 200)
                        console.log(answer.message);

                    this.activateFastReloading(true, true);
                }
            );
        }

        /**
         * Load messages from server
         */
        public loadMessages() : void
        {
            var url : string = this.apiRoot+'chat/'+this.chatID+'/messages/';
            var firstLoading : boolean = true;
            if(this.lastLoadedMessageID > -1)
            {
                url += this.lastLoadedMessageID+'/'+this.lastLoadedWatsonMessageID+'/new/';
                firstLoading = false;
            }

            $.get(url,
                (answer : JSONAnswer_Messages) =>
                {
                    if(answer.messagecount > 0 || answer.watsonmessagecount > 0)
                    {
                        var ui : UI = BWB.getInstance().getUI();
                        var currentUser : string = BWB.getInstance().getUserName();
                        var notificationMessages : BaseMessage[] = [];

                        for(var message of answer.messages)
                        {
                            if(message.id > this.lastLoadedMessageID)
                            {
                                ui.addMessage(message.id, message.text, message.author, message.timestamp);
                                this.lastLoadedMessageID = message.id;
                                if(message.author != currentUser)
                                {
                                    notificationMessages.push(message);
                                    this.activateFastReloading(false);
                                }
                            }
                        }

                        for(var watsonMessage of answer.watsonmessages)
                        {
                            if(watsonMessage.message > -1)
                            {
                                if(watsonMessage.id > this.lastLoadedWatsonMessageID)
                                {
                                    this.lastLoadedWatsonMessageID = watsonMessage.id;
                                    ui.addWatsonAnswer(watsonMessage.id, watsonMessage.text, watsonMessage.system_text_pre, watsonMessage.system_text_post, watsonMessage.confidence, watsonMessage.timestamp, watsonMessage.message);
                                    notificationMessages.push(watsonMessage);
                                    this.activateFastReloading(false);
                                }
                            }
                        }

                        ui.scrollToBottom();

                        if(!firstLoading && notificationMessages.length > 0)
                        {
                            if(notificationMessages.length == 1)
                                ui.showNotification("Watson BWB Chat: New message", bwb.APIConnector._createMessageString(notificationMessages[0], false));
                            else {
                                var body:string = "";
                                for (var nm of notificationMessages)
                                {
                                    if(body != "")
                                        body += "\n";
                                    body += bwb.APIConnector._createMessageString(nm, true);
                                }
                                ui.showNotification("Watson BWB Chat: " + notificationMessages.length + " new messages", body);
                            }
                        }
                    }
                });
        }

        /**
         * Create a string for notification
         *
         * @param message message to parse
         * @param shorten restrict length of the string?
         * @param maxLength maximum length of the string (ignored when shorten is false)
         * @returns {string} formatted string
         * @private
         */
        private static _createMessageString(message: BaseMessage, shorten = false, maxLength = 40) : string
        {
            var s : string = "";

            //Write author (if applicable)
            if(message.hasOwnProperty("author"))
                s += (<Message>message).author+": ";
            else
                s += "Watson: ";

            //Remove html tags
            var rawtext = (message.text != '') ? message.text : (message.hasOwnProperty("system_text_pre") ? (<WatsonMessage>message).system_text_pre : '');
            var text : string = $('<p>').html(rawtext).text();

            //Shorten if necessary
            if(!shorten || text.length < maxLength)
                s += text;
            else
                s += text.substr(0, 39)+"...";

            return s;
        }

        /**
         * Load messages from server
         */
        public loadAnswer() : void
        {
            $.get(this.apiRoot+'expert/answer/',
                (answer : JSONAnswer_ExpertAnswer) =>
                {
                    if(answer.status == 200)
                    {
                        this.lastLoadedWatsonMessageID = answer.answer.id;
                        BWBExpert.getInstance().getUI().setAnswer(answer.answer);
                    }
                });
        }


        /**
         * Vote about the quality of an answer by watson
         */
        public vote(messageId : number, action: string) : void
        {
            $.post(
                this.apiRoot+'message/'+messageId+'/vote/',
                {
                    'action':action,
                },
                (answer: JSONAnswer_Status) => {
                    if(answer.status != 200)
                        console.log(answer.message);
                }
            );
        }

        /**
         * Ask the expert
         */
        public askExpert(question: string) : void
        {
            $.post(
                this.apiRoot+'expert/ask/',
                {
                    'text': question
                },
                (answer: JSONAnswer_Status) => {
                    if(answer.status != 200)
                        BWBExpert.getInstance().getUI().setAnswerFailed();
                    else
                        this.loadAnswer();
                }
            );
        }

        /**
         * Get URL of an audio version of the current watson message
         */
        public getAudioUrl(messageID: number) : string
        {
            return this.apiRoot + 'watsonmessage/' + messageID + '/tospeech/';
        }

        /**
         * Get Example
         */
        public getExample() : void
        {
            $.get(this.apiRoot+'url_parts/',
                (answer : JSONAnswer_Status) =>
                {
                    console.log(answer.status);
                    console.log(answer.message);
                });
        }


        /**
         * Post Example
         */
        public postExample() : void
        {
            $.post(
                this.apiRoot+'url_parts/',
                {
                    'key':"value",
                },
                (answer: JSONAnswer_Status) => {
                    if(answer.status != 200)
                        console.log(answer.message);
                },
                'application/x-www-form-urlencoded; charset=UTF-8'
            );
        }

        /**
         * Check if this HTTP method requires CSRF protection
         *
         * @param method method to test
         * @returns {boolean} true if method needs protection, false if not
         */
        private static csrfSafeMethod(method: string) {
            // these HTTP methods do not require CSRF protection
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        }
    }
}
