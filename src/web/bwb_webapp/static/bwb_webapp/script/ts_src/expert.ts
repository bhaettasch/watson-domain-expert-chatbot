/**
 * BWB BWBExpert
 *
 * @author Benjamin Haettasch
 * @version 0.1
 */

///<reference path='../ext/jquery.d.ts' />

module bwb
{
    export class BWBExpert {

        private apiConnector: APIConnector;
        public csrfToken : string;
        private UI : ExpertUI;

        getAPIConnector() : APIConnector
        {
            return this.apiConnector;
        }

        getUI() : ExpertUI
        {
            return this.UI;
        }

        /**
         * Init the app
         *
         * @param apiRoot URL pointing to API root
         * @param csrfToken token for cross site request forgery protection
         */
        init(apiRoot : string, csrfToken: string)
        {
            this.apiConnector = new APIConnector(apiRoot, 0);
            this.csrfToken = csrfToken;
            this.UI = new ExpertUI();
        }

        /**
         * Singleton instance
         */
        private static _instance : BWBExpert = null;

        /**
         * Constructor
         *
         * Do not call this directly but use getInstance() instead.
         * This object is meant to be a singleton.
         *
         * @private
         */
        constructor() {
            if (BWBExpert._instance) {
                throw new Error("Error: Instantiation failed: Use BWBExpert.getInstance() instead of new.");
            }
        }

        /**
         * Get singleton instance
         *
         * @returns {BWB} singleton instance
         */
        public static getInstance() : BWBExpert
        {
            if(BWBExpert._instance === null) {
                BWBExpert._instance = new BWBExpert();
            }
            return BWBExpert._instance;
        }
    }
}
