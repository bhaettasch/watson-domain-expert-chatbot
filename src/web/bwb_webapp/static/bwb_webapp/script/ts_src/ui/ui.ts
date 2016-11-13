/**
 * SurfaceBeam Web Presentation Module
 *
 * @author Benjamin Haettasch
 * @version 0.1
 */

/// <reference path="../bwb.ts" />
/// <reference path="../../ext/jquery.d.ts" />

module bwb
{
    declare var Notification: any;

    export class UI extends BaseUI
    {
        //jquery reference to input field for own messages
        protected inputMessage : JQuery;
        
        //jquery reference to chat window/area
        protected chatWindow : JQuery;

        /**
         * Constructor
         */
        constructor() {
            super();

            this.inputMessage = $('#inputMessage');
            this.chatWindow = $('#chatWindow');

            // Bind send button
            $('#formMessage').on('submit', (event : Event) => {
                BWB.getInstance().getAPIConnector().sendMessage(this.inputMessage.val());
                this.inputMessage.val("");
                event.preventDefault();
            });
        }

        /**
         * Add a message to chat window
         *
         * @param id message id
         * @param message text of the message
         * @param author author of the message
         * @param timestamp timestamp of the message
         */
        public addMessage(id: number, message: string, author: string, timestamp: string) : void
        {
            this.chatWindow.append('<div id="message_'+id+'" class="message"><div class="message-timestamp">'+timestamp+'</div><b>'+author+'</b><p>'+message+'</p></div>');
        }

        /**
         * Add watson anwer to chat window
         *
         * @param id answer id
         * @param message text of the message
         * @param system_text_pre text to display before the actual message
         * @param system_text_post text to display after the actual message
         * @param confidence
         * @param timestamp timestamp of the message
         * @param messageid corresponding message id (the one that this is an answer to)
         */
        public addWatsonAnswer(id: number, message: string, system_text_pre : string, system_text_post : string, confidence: number, timestamp: string, messageid: number) : void
        {
            var system_pre_formatted : string = system_text_pre != "" ? system_text_pre + '<br>' : "";
            var system_post_formatted : string = system_text_post != "" ? '<br>' + system_text_post : "";
            var play_formatted : string = message != '' ? '<i class="fa fa-volume-off fa-fw play play-'+id+'" aria-hidden="true"></i>&nbsp;&nbsp;&nbsp;' : '';
            var confidence_formatted : string = confidence > 0 ? "&nbsp;&nbsp;&nbsp;Confidence: " + (confidence * 100).toFixed(2) + "%" : "";

            var node : string =   '<div class="message message-watson">'
                                + '<div id="message_watson_'+id+'" class="message-timestamp">'+timestamp+'</div>'
                                + '<b><i class="fa fa-sellsy" aria-hidden="true"></i> Watson</b>'
                                + '<p class="message-content">'+system_pre_formatted + message + system_post_formatted+'</p>'
                                + '<div class="message-votebox">'
                                + play_formatted
                                + 'Correct: <i class="fa fa-thumbs-o-up fa-fw vote vote-'+id+' vote-correct" aria-hidden="true" bwb-action="correct"></i> '
                                + '<i class="fa fa-thumbs-o-down vote fa-fw fa-flip-horizontal vote-'+id+' vote-correct" aria-hidden="true" bwb-action="incorrect"></i>&nbsp;&nbsp;&nbsp;'
                                + 'Helpful: <i class="fa fa-thumbs-o-up fa-fw vote vote-'+id+' vote-helpful" aria-hidden="true" bwb-action="helpful"></i> '
                                + '<i class="fa fa-thumbs-o-down fa-fw fa-flip-horizontal vote vote-'+id+' vote-helpful" aria-hidden="true" bwb-action="nothelpful"></i>'
                                + confidence_formatted
                                + '</div></div>';
            $(node).insertAfter($('#message_'+messageid));
            $('.vote-'+id).on('click', (event: Event) => {
                var action : string = $(event.currentTarget).attr('bwb-action');
                BWB.getInstance().getAPIConnector().vote(id, action);
                switch(action) {
                    case "correct":
                        $(event.currentTarget).removeClass('fa-thumbs-o-up').addClass('fa-thumbs-up');
                        $('.vote-correct.vote-'+id).off('click');
                        break;
                    case "incorrect":
                        $(event.currentTarget).removeClass('fa-thumbs-o-down').addClass('fa-thumbs-down');
                        $('.vote-correct.vote-'+id).off('click');
                        break;
                    case "helpful":
                        $(event.currentTarget).removeClass('fa-thumbs-o-up').addClass('fa-thumbs-up');
                        $('.vote-helpful.vote-'+id).off('click');
                        break;
                    case "nothelpful":
                        $(event.currentTarget).removeClass('fa-thumbs-o-down').addClass('fa-thumbs-down');
                        $('.vote-helpful.vote-'+id).off('click');
                        break;
                }
            });
            $('.play-'+id).on('click', (event: Event) => {
                var bwb : BWB = BWB.getInstance();
                if($(event.currentTarget).hasClass('fa-volume-off'))
                {
                    this.playAudio(BWB.getInstance().getAPIConnector().getAudioUrl(id));
                    $(event.currentTarget).removeClass('fa-volume-off').addClass('fa-volume-up');
                }
                else
                {
                    this.stopAudio();
                    $(event.currentTarget).removeClass('fa-volume-up').addClass('fa-volume-off');
                }
            })
        }

        /**
         * Scroll chat window to bottom (with a little animation)
         */
        public scrollToBottom() : void
        {
            this.chatWindow.animate({scrollTop:this.chatWindow[0].scrollHeight}, 250);
        }
    }
}
