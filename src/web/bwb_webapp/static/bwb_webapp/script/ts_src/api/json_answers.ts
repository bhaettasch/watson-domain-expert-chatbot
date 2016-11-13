/**
 * SurfaceBeam Web Presentation Module
 *
 * @author Benjamin Haettasch
 * @version 0.1
 */

module bwb
{
    export interface JSONAnswer_Status {
        status: number;
        message: string;
    }

    export interface JSONAnswer_Messages {
        messagecount: number;
        messages: Message[];
        watsonmessagecount: number;
        watsonmessages: WatsonMessage[];
        status: number;
    }

    export interface BaseMessage {
        id: number;
        text: string;
        timestamp: string;
    }

    export interface Message extends BaseMessage{
        author: string;
    }

    export interface WatsonMessage extends BaseMessage{
        message: number;
        system_text_pre: string;
        system_text_post: string;
        confidence: number;
    }

    export interface JSONAnswer_ExpertAnswer {
        status: number;
        answer: WatsonMessage;
    }
}