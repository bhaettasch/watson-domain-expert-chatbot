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

    export class BaseUI
    {

        public audioPlayer: HTMLAudioElement;

        /**
         * Constructor
         */
        constructor() {
            // Create audio player
            this.audioPlayer = document.createElement('audio');
            this.audioPlayer.addEventListener('ended', () => {
                $('.fa-volume-up').removeClass('fa-volume-up').addClass('fa-volume-off');
            });

            $(document).on('click', '.img-thumbnail', (e: Event) => {
                $('.imagepreview').attr('src', $(e.currentTarget).attr('src'));
                (<any>$('#imagemodal')).modal('show');
            });
        }

        /**
         * Create notification
         *
         * @param title title of the notification
         * @param text body text of the notification
         */
        public showNotification(title: string, text: string) : void
        {
            // Let's check if the browser supports notifications
            if (!("Notification" in window)) {
                console.log("This browser does not support desktop notification");
                return;
            }

            // Let's check whether notification permissions have alredy been granted
            else if (Notification.permission === "granted") {
                // If it's okay let's create a notification
                this._createNotification(title, text);
            }

            // Otherwise, we need to ask the user for permission
            else if (Notification.permission !== 'denied') {
                Notification.requestPermission((permission : string) => {
                    // If the user accepts, let's create a notification
                    if (permission === "granted") {
                        this._createNotification(title, text);
                    }
                });
            }
        }

        /**
         * Create notification (without checking, if it is possible and without requirement check
         *
         * @param title title of the notification
         * @param text body text of the notification
         */
        private _createNotification(title: string, text: string) : void
        {
            var notification = new Notification(title, {body: text});
        }

        /**
         * Play the given audiofile
         * @param url file to play
         */
        public playAudio(url: string) : void
        {
            if (this.audioPlayer.canPlayType('audio/ogg')) {
                this.audioPlayer.setAttribute('src', url);
                this.audioPlayer.play();
            }
        }

        /**
         * Stop the current audio playing (if any)
         */
        public stopAudio() : void
        {
            this.audioPlayer.pause();
        }
    }
}
