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
    declare var WebAudioRecorder: any;

    export class ExpertUI extends BaseUI
    {
        //jquery reference to input field for own messages
        private questionInput : JQuery;

        //jquery reference to input field for own messages
        private questionArea : JQuery;
        
        //jquery reference to chat window/area
        private answerArea : JQuery;

        private confidenceArea : JQuery;
        private confidenceField : JQuery;

        private voteArea : JQuery;

        private audioRecorder: HTMLAudioElement;

        private audioPlayerControl: JQuery;

        private voted_correct : boolean;
        private voted_helpful : boolean;

        /**
         * Constructor
         */
        constructor() {
            super();

            this.questionInput = $('#inputQuestion');
            this.questionArea = $('#questionArea');
            this.answerArea = $('#answerAreaInner');
            this.confidenceArea = $('#confidenceArea');
            this.confidenceField = $('#confidenceField');
            this.voteArea = $('#voteArea');
            this.audioPlayerControl = $('#playButton');

            // Bind send button
            $('#formMessage').on('submit', (event : Event) => {
                var question : string = this.questionInput.val().trim();
                if(question != '')
                {
                    this.questionInput.val("");
                    this.questionArea.html(question);
                    this.answerArea.html('<i class="fa fa-cog fa-spin fa-5x" aria-hidden="true"></i>');
                    BWBExpert.getInstance().getAPIConnector().askExpert(question);
                }
                event.preventDefault();
            });

            this.audioRecorder = document.createElement('audio');


            $('.vote').on('click', (event: Event) => {
                var action: string = $(event.currentTarget).attr('bwb-action');
                if((action=='correct' || action=='incorrect') && !this.voted_correct)
                {
                    this.voted_correct = true;
                    BWBExpert.getInstance().getAPIConnector().vote(BWBExpert.getInstance().getAPIConnector().lastLoadedWatsonMessageID, action);
                    if($(event.currentTarget).hasClass('fa-thumbs-o-down'))
                        $(event.currentTarget).removeClass('fa-thumbs-o-down').addClass('fa-thumbs-down');
                    else
                        $(event.currentTarget).removeClass('fa-thumbs-o-up').addClass('fa-thumbs-up');
                }
                else if((action=='helpful' || action=='nothelpful') && !this.voted_helpful)
                {
                    this.voted_helpful = true;
                    BWBExpert.getInstance().getAPIConnector().vote(BWBExpert.getInstance().getAPIConnector().lastLoadedWatsonMessageID, action);
                    if($(event.currentTarget).hasClass('fa-thumbs-o-down'))
                        $(event.currentTarget).removeClass('fa-thumbs-o-down').addClass('fa-thumbs-down');
                    else
                        $(event.currentTarget).removeClass('fa-thumbs-o-up').addClass('fa-thumbs-up');
                }
            });
            $('.play').on('click', (event: Event) => {
                if($(event.currentTarget).hasClass('fa-volume-off'))
                {
                    this.playAudio(BWBExpert.getInstance().getAPIConnector().getAudioUrl(BWBExpert.getInstance().getAPIConnector().lastLoadedWatsonMessageID));
                    $(event.currentTarget).removeClass('fa-volume-off').addClass('fa-volume-up');
                }
                else
                {
                    this.stopAudio();
                    $(event.currentTarget).removeClass('fa-volume-up').addClass('fa-volume-off');
                }
            });

            $(document).on('click', '.img-thumbnail', (e: Event) => {
                $('.imagepreview').attr('src', $(e.currentTarget).attr('src'));
                (<any>$('#imagemodal')).modal('show');
            });
        }

        /**
         * Add a message to chat window
         *
         * @param answer answer by watson
         */
        public setAnswer(answer: WatsonMessage) : void {
            var system_pre_formatted:string = answer.system_text_pre != "" ? answer.system_text_pre + ' <br><br>' : "";
            var system_post_formatted:string = answer.system_text_post != "" ? '<br><br>' + answer.system_text_post : "";

            this.answerArea.html(system_pre_formatted + answer.text + system_post_formatted);
            this.confidenceField.html((answer.confidence * 100).toFixed(2));
            this.voteArea.css('visibility', 'visible');

            this.voted_correct = false;
            this.voted_helpful = false;
            $('.fa-thumbs-down').removeClass('fa-thumbs-down').addClass('fa-thumbs-o-down');
            $('.fa-thumbs-up').removeClass('fa-thumbs-up').addClass('fa-thumbs-o-up');

            if(answer.text != '')
                this.audioPlayerControl.show();
            else
                this.audioPlayerControl.hide();

            if(answer.confidence > 0)
                this.confidenceArea.show();
            else
                this.confidenceArea.hide();
        }

        /**
         * Display error message in answer area
         */
        public setAnswerFailed() : void {
            this.answerArea.html('Sorry, something wrent wrong. Please try again');
            this.voteArea.css('visibility', 'hidden');
        }
    }
}
