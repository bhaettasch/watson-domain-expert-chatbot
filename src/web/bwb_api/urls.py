from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from . import views

urlpatterns = [
    url(r'^chat/(?P<pk>[0-9]+)/messages/$', views.NewMessagesView.as_view(), name='chat_messages'),
    url(r'^chat/(?P<pk>[0-9]+)/messages/(?P<lastMessageID>[0-9]+)/(?P<lastWatsonMessageID>[0-9]+)/new/$', views.NewMessagesView.as_view(), name='chat_newmessages'),
    url(r'^chat/messages/add/$', views.AddMessageView.as_view(), name='chat_addmessage'),
    url(r'^message/(?P<pk>[0-9]+)/vote/$', csrf_exempt(views.VoteView.as_view()), name="message_vote"),
    url(r'^watsonmessage/(?P<pk>[0-9]+)/tospeech/$', views.WatsonMessageToSpeechView.as_view(), name="watsonmessage_tospeech"),

    url(r'^fact/add/$', csrf_exempt(views.AddFactView.as_view()), name="fact_add"),

    #API endpoints -- no CSRF protection
    url(r'^external/chat/(?P<pk>[0-9]+)/answers/$', views.NewWatsonMessagesView.as_view(), name='ext_chat_answers'),
    url(r'^external/chat/(?P<pk>[0-9]+)/answers/(?P<lastMessageID>[0-9]+)/new/$', views.NewWatsonMessagesView.as_view(), name='ext_chat_newmessages'),
    url(r'^external/chat/post/$', csrf_exempt(views.AddMessageView.as_view()), name='ext_chat_postmessage'),
    url(r'^external/chat/create/$', csrf_exempt(views.CreateExternalChatView.as_view()), name='ext_chat_create'),
    url(r'^external/speech/totext/url/$', csrf_exempt(views.AudioURLToTextView.as_view()), name='ext_s2t_url'),
    url(r'^external/speech/totext/$', csrf_exempt(views.AudioURLToTextView.as_view()), name='ext_s2t'),
    url(r'^external/message/(?P<pk>[0-9]+)/vote/$', csrf_exempt(views.VoteView.as_view()), name="message_vote"),

    url(r'^expert/ask/$', csrf_exempt(views.ExpertAskView.as_view()), name='expert_ask'),
    url(r'^expert/answer/$', views.ExpertAnswerView.as_view(), name='expert_answer'),

    url(r'^speech/totext/url/$', csrf_exempt(views.AudioURLToTextView.as_view()), name='s2t_url'),
    url(r'^speech/totext/$', csrf_exempt(views.AudioURLToTextView.as_view()), name='s2t'),
]
