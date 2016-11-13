/// <reference path="../ext/jquery.d.ts" />
declare module bwb {
    class BWB {
        private apiConnector;
        csrfToken: string;
        private UI;
        private user;
        getAPIConnector(): APIConnector;
        getUI(): UI;
        getUserName(): string;
        init(apiRoot: string, chatID: number, csrfToken: string, user: string): void;
        private static _instance;
        constructor();
        static getInstance(): BWB;
    }
}
declare module bwb {
    interface JSONAnswer_Status {
        status: number;
        message: string;
    }
    interface JSONAnswer_Messages {
        messagecount: number;
        messages: Message[];
        watsonmessagecount: number;
        watsonmessages: WatsonMessage[];
        status: number;
    }
    interface BaseMessage {
        id: number;
        text: string;
        timestamp: string;
    }
    interface Message extends BaseMessage {
        author: string;
    }
    interface WatsonMessage extends BaseMessage {
        message: number;
        system_text_pre: string;
        system_text_post: string;
        confidence: number;
    }
    interface JSONAnswer_ExpertAnswer {
        status: number;
        answer: WatsonMessage;
    }
}
declare module bwb {
    class APIConnector {
        private apiRoot;
        private chatID;
        lastLoadedMessageID: number;
        lastLoadedWatsonMessageID: number;
        messageLoadingInterval: number;
        fastReload: boolean;
        constructor(apiRoot: string, chatID: number);
        start(): void;
        private startMessageLoadingInterval(reloadNow?);
        private activateFastReloading(fast, reloadNow?);
        sendMessage(message: string): void;
        loadMessages(): void;
        private static _createMessageString(message, shorten?, maxLength?);
        loadAnswer(): void;
        vote(messageId: number, action: string): void;
        askExpert(question: string): void;
        getAudioUrl(messageID: number): string;
        getExample(): void;
        postExample(): void;
        private static csrfSafeMethod(method);
    }
}
declare module bwb {
    class BWBExpert {
        private apiConnector;
        csrfToken: string;
        private UI;
        getAPIConnector(): APIConnector;
        getUI(): ExpertUI;
        init(apiRoot: string, csrfToken: string): void;
        private static _instance;
        constructor();
        static getInstance(): BWBExpert;
    }
}
declare module bwb {
    class BaseUI {
        audioPlayer: HTMLAudioElement;
        constructor();
        showNotification(title: string, text: string): void;
        private _createNotification(title, text);
        playAudio(url: string): void;
        stopAudio(): void;
    }
}
declare module bwb {
    class UI extends BaseUI {
        protected inputMessage: JQuery;
        protected chatWindow: JQuery;
        constructor();
        addMessage(id: number, message: string, author: string, timestamp: string): void;
        addWatsonAnswer(id: number, message: string, system_text_pre: string, system_text_post: string, confidence: number, timestamp: string, messageid: number): void;
        scrollToBottom(): void;
    }
}
declare module bwb {
    class ExpertUI extends BaseUI {
        private questionInput;
        private questionArea;
        private answerArea;
        private confidenceArea;
        private confidenceField;
        private voteArea;
        private audioRecorder;
        private audioPlayerControl;
        private voted_correct;
        private voted_helpful;
        constructor();
        setAnswer(answer: WatsonMessage): void;
        setAnswerFailed(): void;
    }
}
