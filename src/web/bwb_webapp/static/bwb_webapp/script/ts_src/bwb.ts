/**
 * BWB Main app class
 *
 * @author Benjamin Haettasch
 * @version 0.1
 */

///<reference path='../ext/jquery.d.ts' />

module bwb
{
    export class BWB {

        private apiConnector: APIConnector;
        public csrfToken : string;
        private UI : UI;
        private user : string;

        getAPIConnector() : APIConnector
        {
            return this.apiConnector;
        }

        getUI() : UI
        {
            return this.UI;
        }

        getUserName() : string
        {
            return this.user;
        }

        /**
         * Init the app
         *
         * @param apiRoot URL pointing to API root
         * @param chatID ID of the current chat
         * @param csrfToken token for cross site request forgery protection
         * @param user name of the current user
         */
        init(apiRoot : string, chatID : number, csrfToken: string, user: string)
        {
            this.user = user;
            this.apiConnector = new APIConnector(apiRoot, chatID);
            this.csrfToken = csrfToken;
            this.UI = new UI();

            this.apiConnector.start();
        }

        /**
         * Singleton instance
         */
        private static _instance : BWB = null;

        /**
         * Constructor
         *
         * Do not call this directly but use getInstance() instead.
         * This object is meant to be a singleton.
         *
         * @private
         */
        constructor() {
            if (BWB._instance) {
                throw new Error("Error: Instantiation failed: Use SurfaceBeam.getInstance() instead of new.");
            }
        }

        /**
         * Get singleton instance
         *
         * @returns {BWB} singleton instance
         */
        public static getInstance() : BWB
        {
            if(BWB._instance === null) {
                BWB._instance = new BWB();
            }
            return BWB._instance;
        }
    }
}
