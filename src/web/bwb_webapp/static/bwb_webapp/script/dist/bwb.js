var __extends = (this && this.__extends) || function (d, b) {
    for (var p in b) if (b.hasOwnProperty(p)) d[p] = b[p];
    function __() { this.constructor = d; }
    d.prototype = b === null ? Object.create(b) : (__.prototype = b.prototype, new __());
};
var bwb;
(function (bwb) {
    var BWB = (function () {
        function BWB() {
            if (BWB._instance) {
                throw new Error("Error: Instantiation failed: Use SurfaceBeam.getInstance() instead of new.");
            }
        }
        BWB.prototype.getAPIConnector = function () {
            return this.apiConnector;
        };
        BWB.prototype.getUI = function () {
            return this.UI;
        };
        BWB.prototype.getUserName = function () {
            return this.user;
        };
        BWB.prototype.init = function (apiRoot, chatID, csrfToken, user) {
            this.user = user;
            this.apiConnector = new bwb.APIConnector(apiRoot, chatID);
            this.csrfToken = csrfToken;
            this.UI = new bwb.UI();
            this.apiConnector.start();
        };
        BWB.getInstance = function () {
            if (BWB._instance === null) {
                BWB._instance = new BWB();
            }
            return BWB._instance;
        };
        BWB._instance = null;
        return BWB;
    }());
    bwb.BWB = BWB;
})(bwb || (bwb = {}));
var bwb;
(function (bwb) {
    var APIConnector = (function () {
        function APIConnector(apiRoot, chatID) {
            this.apiRoot = apiRoot;
            this.chatID = chatID;
            this.lastLoadedMessageID = -1;
            this.lastLoadedWatsonMessageID = 0;
            this.fastReload = false;
            $.ajaxSetup({
                beforeSend: function (xhr, settings) {
                    if (!APIConnector.csrfSafeMethod(settings.type) && !this.crossDomain) {
                        xhr.setRequestHeader("X-CSRFToken", bwb.BWB.getInstance().csrfToken);
                    }
                }
            });
        }
        APIConnector.prototype.start = function () {
            this.startMessageLoadingInterval();
        };
        APIConnector.prototype.startMessageLoadingInterval = function (reloadNow) {
            var _this = this;
            if (reloadNow === void 0) { reloadNow = true; }
            if (this.messageLoadingInterval != 0)
                window.clearInterval(this.messageLoadingInterval);
            if (reloadNow)
                this.loadMessages();
            this.messageLoadingInterval = window.setInterval(function () { _this.loadMessages(); }, this.fastReload ? 500 : 2000);
        };
        APIConnector.prototype.activateFastReloading = function (fast, reloadNow) {
            if (reloadNow === void 0) { reloadNow = false; }
            if (this.fastReload != fast) {
                this.fastReload = fast;
                this.startMessageLoadingInterval(reloadNow);
            }
        };
        APIConnector.prototype.sendMessage = function (message) {
            var _this = this;
            $.post(this.apiRoot + 'chat/messages/add/', {
                'text': message,
                'chat': this.chatID
            }, function (answer) {
                if (answer.status != 200)
                    console.log(answer.message);
                _this.activateFastReloading(true, true);
            });
        };
        APIConnector.prototype.loadMessages = function () {
            var _this = this;
            var url = this.apiRoot + 'chat/' + this.chatID + '/messages/';
            var firstLoading = true;
            if (this.lastLoadedMessageID > -1) {
                url += this.lastLoadedMessageID + '/' + this.lastLoadedWatsonMessageID + '/new/';
                firstLoading = false;
            }
            $.get(url, function (answer) {
                if (answer.messagecount > 0 || answer.watsonmessagecount > 0) {
                    var ui = bwb.BWB.getInstance().getUI();
                    var currentUser = bwb.BWB.getInstance().getUserName();
                    var notificationMessages = [];
                    for (var _i = 0, _a = answer.messages; _i < _a.length; _i++) {
                        var message = _a[_i];
                        if (message.id > _this.lastLoadedMessageID) {
                            ui.addMessage(message.id, message.text, message.author, message.timestamp);
                            _this.lastLoadedMessageID = message.id;
                            if (message.author != currentUser) {
                                notificationMessages.push(message);
                                _this.activateFastReloading(false);
                            }
                        }
                    }
                    for (var _b = 0, _c = answer.watsonmessages; _b < _c.length; _b++) {
                        var watsonMessage = _c[_b];
                        if (watsonMessage.message > -1) {
                            if (watsonMessage.id > _this.lastLoadedWatsonMessageID) {
                                _this.lastLoadedWatsonMessageID = watsonMessage.id;
                                ui.addWatsonAnswer(watsonMessage.id, watsonMessage.text, watsonMessage.system_text_pre, watsonMessage.system_text_post, watsonMessage.confidence, watsonMessage.timestamp, watsonMessage.message);
                                notificationMessages.push(watsonMessage);
                                _this.activateFastReloading(false);
                            }
                        }
                    }
                    ui.scrollToBottom();
                    if (!firstLoading && notificationMessages.length > 0) {
                        if (notificationMessages.length == 1)
                            ui.showNotification("Watson BWB Chat: New message", bwb.APIConnector._createMessageString(notificationMessages[0], false));
                        else {
                            var body = "";
                            for (var _d = 0, notificationMessages_1 = notificationMessages; _d < notificationMessages_1.length; _d++) {
                                var nm = notificationMessages_1[_d];
                                if (body != "")
                                    body += "\n";
                                body += bwb.APIConnector._createMessageString(nm, true);
                            }
                            ui.showNotification("Watson BWB Chat: " + notificationMessages.length + " new messages", body);
                        }
                    }
                }
            });
        };
        APIConnector._createMessageString = function (message, shorten, maxLength) {
            if (shorten === void 0) { shorten = false; }
            if (maxLength === void 0) { maxLength = 40; }
            var s = "";
            if (message.hasOwnProperty("author"))
                s += message.author + ": ";
            else
                s += "Watson: ";
            var rawtext = (message.text != '') ? message.text : (message.hasOwnProperty("system_text_pre") ? message.system_text_pre : '');
            var text = $('<p>').html(rawtext).text();
            if (!shorten || text.length < maxLength)
                s += text;
            else
                s += text.substr(0, 39) + "...";
            return s;
        };
        APIConnector.prototype.loadAnswer = function () {
            var _this = this;
            $.get(this.apiRoot + 'expert/answer/', function (answer) {
                if (answer.status == 200) {
                    _this.lastLoadedWatsonMessageID = answer.answer.id;
                    bwb.BWBExpert.getInstance().getUI().setAnswer(answer.answer);
                }
            });
        };
        APIConnector.prototype.vote = function (messageId, action) {
            $.post(this.apiRoot + 'message/' + messageId + '/vote/', {
                'action': action,
            }, function (answer) {
                if (answer.status != 200)
                    console.log(answer.message);
            });
        };
        APIConnector.prototype.askExpert = function (question) {
            var _this = this;
            $.post(this.apiRoot + 'expert/ask/', {
                'text': question
            }, function (answer) {
                if (answer.status != 200)
                    bwb.BWBExpert.getInstance().getUI().setAnswerFailed();
                else
                    _this.loadAnswer();
            });
        };
        APIConnector.prototype.getAudioUrl = function (messageID) {
            return this.apiRoot + 'watsonmessage/' + messageID + '/tospeech/';
        };
        APIConnector.prototype.getExample = function () {
            $.get(this.apiRoot + 'url_parts/', function (answer) {
                console.log(answer.status);
                console.log(answer.message);
            });
        };
        APIConnector.prototype.postExample = function () {
            $.post(this.apiRoot + 'url_parts/', {
                'key': "value",
            }, function (answer) {
                if (answer.status != 200)
                    console.log(answer.message);
            }, 'application/x-www-form-urlencoded; charset=UTF-8');
        };
        APIConnector.csrfSafeMethod = function (method) {
            return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
        };
        return APIConnector;
    }());
    bwb.APIConnector = APIConnector;
})(bwb || (bwb = {}));
var bwb;
(function (bwb) {
    var BWBExpert = (function () {
        function BWBExpert() {
            if (BWBExpert._instance) {
                throw new Error("Error: Instantiation failed: Use BWBExpert.getInstance() instead of new.");
            }
        }
        BWBExpert.prototype.getAPIConnector = function () {
            return this.apiConnector;
        };
        BWBExpert.prototype.getUI = function () {
            return this.UI;
        };
        BWBExpert.prototype.init = function (apiRoot, csrfToken) {
            this.apiConnector = new bwb.APIConnector(apiRoot, 0);
            this.csrfToken = csrfToken;
            this.UI = new bwb.ExpertUI();
        };
        BWBExpert.getInstance = function () {
            if (BWBExpert._instance === null) {
                BWBExpert._instance = new BWBExpert();
            }
            return BWBExpert._instance;
        };
        BWBExpert._instance = null;
        return BWBExpert;
    }());
    bwb.BWBExpert = BWBExpert;
})(bwb || (bwb = {}));
var bwb;
(function (bwb) {
    var BaseUI = (function () {
        function BaseUI() {
            this.audioPlayer = document.createElement('audio');
            this.audioPlayer.addEventListener('ended', function () {
                $('.fa-volume-up').removeClass('fa-volume-up').addClass('fa-volume-off');
            });
            $(document).on('click', '.img-thumbnail', function (e) {
                $('.imagepreview').attr('src', $(e.currentTarget).attr('src'));
                $('#imagemodal').modal('show');
            });
        }
        BaseUI.prototype.showNotification = function (title, text) {
            var _this = this;
            if (!("Notification" in window)) {
                console.log("This browser does not support desktop notification");
                return;
            }
            else if (Notification.permission === "granted") {
                this._createNotification(title, text);
            }
            else if (Notification.permission !== 'denied') {
                Notification.requestPermission(function (permission) {
                    if (permission === "granted") {
                        _this._createNotification(title, text);
                    }
                });
            }
        };
        BaseUI.prototype._createNotification = function (title, text) {
            var notification = new Notification(title, { body: text });
        };
        BaseUI.prototype.playAudio = function (url) {
            if (this.audioPlayer.canPlayType('audio/ogg')) {
                this.audioPlayer.setAttribute('src', url);
                this.audioPlayer.play();
            }
        };
        BaseUI.prototype.stopAudio = function () {
            this.audioPlayer.pause();
        };
        return BaseUI;
    }());
    bwb.BaseUI = BaseUI;
})(bwb || (bwb = {}));
var bwb;
(function (bwb_1) {
    var UI = (function (_super) {
        __extends(UI, _super);
        function UI() {
            var _this = this;
            _super.call(this);
            this.inputMessage = $('#inputMessage');
            this.chatWindow = $('#chatWindow');
            $('#formMessage').on('submit', function (event) {
                bwb_1.BWB.getInstance().getAPIConnector().sendMessage(_this.inputMessage.val());
                _this.inputMessage.val("");
                event.preventDefault();
            });
        }
        UI.prototype.addMessage = function (id, message, author, timestamp) {
            this.chatWindow.append('<div id="message_' + id + '" class="message"><div class="message-timestamp">' + timestamp + '</div><b>' + author + '</b><p>' + message + '</p></div>');
        };
        UI.prototype.addWatsonAnswer = function (id, message, system_text_pre, system_text_post, confidence, timestamp, messageid) {
            var _this = this;
            var system_pre_formatted = system_text_pre != "" ? system_text_pre + '<br>' : "";
            var system_post_formatted = system_text_post != "" ? '<br>' + system_text_post : "";
            var play_formatted = message != '' ? '<i class="fa fa-volume-off fa-fw play play-' + id + '" aria-hidden="true"></i>&nbsp;&nbsp;&nbsp;' : '';
            var confidence_formatted = confidence > 0 ? "&nbsp;&nbsp;&nbsp;Confidence: " + (confidence * 100).toFixed(2) + "%" : "";
            var node = '<div class="message message-watson">'
                + '<div id="message_watson_' + id + '" class="message-timestamp">' + timestamp + '</div>'
                + '<b><i class="fa fa-sellsy" aria-hidden="true"></i> Watson</b>'
                + '<p class="message-content">' + system_pre_formatted + message + system_post_formatted + '</p>'
                + '<div class="message-votebox">'
                + play_formatted
                + 'Correct: <i class="fa fa-thumbs-o-up fa-fw vote vote-' + id + ' vote-correct" aria-hidden="true" bwb-action="correct"></i> '
                + '<i class="fa fa-thumbs-o-down vote fa-fw fa-flip-horizontal vote-' + id + ' vote-correct" aria-hidden="true" bwb-action="incorrect"></i>&nbsp;&nbsp;&nbsp;'
                + 'Helpful: <i class="fa fa-thumbs-o-up fa-fw vote vote-' + id + ' vote-helpful" aria-hidden="true" bwb-action="helpful"></i> '
                + '<i class="fa fa-thumbs-o-down fa-fw fa-flip-horizontal vote vote-' + id + ' vote-helpful" aria-hidden="true" bwb-action="nothelpful"></i>'
                + confidence_formatted
                + '</div></div>';
            $(node).insertAfter($('#message_' + messageid));
            $('.vote-' + id).on('click', function (event) {
                var action = $(event.currentTarget).attr('bwb-action');
                bwb_1.BWB.getInstance().getAPIConnector().vote(id, action);
                switch (action) {
                    case "correct":
                        $(event.currentTarget).removeClass('fa-thumbs-o-up').addClass('fa-thumbs-up');
                        $('.vote-correct.vote-' + id).off('click');
                        break;
                    case "incorrect":
                        $(event.currentTarget).removeClass('fa-thumbs-o-down').addClass('fa-thumbs-down');
                        $('.vote-correct.vote-' + id).off('click');
                        break;
                    case "helpful":
                        $(event.currentTarget).removeClass('fa-thumbs-o-up').addClass('fa-thumbs-up');
                        $('.vote-helpful.vote-' + id).off('click');
                        break;
                    case "nothelpful":
                        $(event.currentTarget).removeClass('fa-thumbs-o-down').addClass('fa-thumbs-down');
                        $('.vote-helpful.vote-' + id).off('click');
                        break;
                }
            });
            $('.play-' + id).on('click', function (event) {
                var bwb = bwb_1.BWB.getInstance();
                if ($(event.currentTarget).hasClass('fa-volume-off')) {
                    _this.playAudio(bwb_1.BWB.getInstance().getAPIConnector().getAudioUrl(id));
                    $(event.currentTarget).removeClass('fa-volume-off').addClass('fa-volume-up');
                }
                else {
                    _this.stopAudio();
                    $(event.currentTarget).removeClass('fa-volume-up').addClass('fa-volume-off');
                }
            });
        };
        UI.prototype.scrollToBottom = function () {
            this.chatWindow.animate({ scrollTop: this.chatWindow[0].scrollHeight }, 250);
        };
        return UI;
    }(bwb_1.BaseUI));
    bwb_1.UI = UI;
})(bwb || (bwb = {}));
var bwb;
(function (bwb) {
    var ExpertUI = (function (_super) {
        __extends(ExpertUI, _super);
        function ExpertUI() {
            var _this = this;
            _super.call(this);
            this.questionInput = $('#inputQuestion');
            this.questionArea = $('#questionArea');
            this.answerArea = $('#answerAreaInner');
            this.confidenceArea = $('#confidenceArea');
            this.confidenceField = $('#confidenceField');
            this.voteArea = $('#voteArea');
            this.audioPlayerControl = $('#playButton');
            $('#formMessage').on('submit', function (event) {
                var question = _this.questionInput.val().trim();
                if (question != '') {
                    _this.questionInput.val("");
                    _this.questionArea.html(question);
                    _this.answerArea.html('<i class="fa fa-cog fa-spin fa-5x" aria-hidden="true"></i>');
                    bwb.BWBExpert.getInstance().getAPIConnector().askExpert(question);
                }
                event.preventDefault();
            });
            this.audioRecorder = document.createElement('audio');
            $('.vote').on('click', function (event) {
                var action = $(event.currentTarget).attr('bwb-action');
                if ((action == 'correct' || action == 'incorrect') && !_this.voted_correct) {
                    _this.voted_correct = true;
                    bwb.BWBExpert.getInstance().getAPIConnector().vote(bwb.BWBExpert.getInstance().getAPIConnector().lastLoadedWatsonMessageID, action);
                    if ($(event.currentTarget).hasClass('fa-thumbs-o-down'))
                        $(event.currentTarget).removeClass('fa-thumbs-o-down').addClass('fa-thumbs-down');
                    else
                        $(event.currentTarget).removeClass('fa-thumbs-o-up').addClass('fa-thumbs-up');
                }
                else if ((action == 'helpful' || action == 'nothelpful') && !_this.voted_helpful) {
                    _this.voted_helpful = true;
                    bwb.BWBExpert.getInstance().getAPIConnector().vote(bwb.BWBExpert.getInstance().getAPIConnector().lastLoadedWatsonMessageID, action);
                    if ($(event.currentTarget).hasClass('fa-thumbs-o-down'))
                        $(event.currentTarget).removeClass('fa-thumbs-o-down').addClass('fa-thumbs-down');
                    else
                        $(event.currentTarget).removeClass('fa-thumbs-o-up').addClass('fa-thumbs-up');
                }
            });
            $('.play').on('click', function (event) {
                if ($(event.currentTarget).hasClass('fa-volume-off')) {
                    _this.playAudio(bwb.BWBExpert.getInstance().getAPIConnector().getAudioUrl(bwb.BWBExpert.getInstance().getAPIConnector().lastLoadedWatsonMessageID));
                    $(event.currentTarget).removeClass('fa-volume-off').addClass('fa-volume-up');
                }
                else {
                    _this.stopAudio();
                    $(event.currentTarget).removeClass('fa-volume-up').addClass('fa-volume-off');
                }
            });
            $(document).on('click', '.img-thumbnail', function (e) {
                $('.imagepreview').attr('src', $(e.currentTarget).attr('src'));
                $('#imagemodal').modal('show');
            });
        }
        ExpertUI.prototype.setAnswer = function (answer) {
            var system_pre_formatted = answer.system_text_pre != "" ? answer.system_text_pre + ' <br><br>' : "";
            var system_post_formatted = answer.system_text_post != "" ? '<br><br>' + answer.system_text_post : "";
            this.answerArea.html(system_pre_formatted + answer.text + system_post_formatted);
            this.confidenceField.html((answer.confidence * 100).toFixed(2));
            this.voteArea.css('visibility', 'visible');
            this.voted_correct = false;
            this.voted_helpful = false;
            $('.fa-thumbs-down').removeClass('fa-thumbs-down').addClass('fa-thumbs-o-down');
            $('.fa-thumbs-up').removeClass('fa-thumbs-up').addClass('fa-thumbs-o-up');
            if (answer.text != '')
                this.audioPlayerControl.show();
            else
                this.audioPlayerControl.hide();
            if (answer.confidence > 0)
                this.confidenceArea.show();
            else
                this.confidenceArea.hide();
        };
        ExpertUI.prototype.setAnswerFailed = function () {
            this.answerArea.html('Sorry, something wrent wrong. Please try again');
            this.voteArea.css('visibility', 'hidden');
        };
        return ExpertUI;
    }(bwb.BaseUI));
    bwb.ExpertUI = ExpertUI;
})(bwb || (bwb = {}));
//# sourceMappingURL=bwb.js.map