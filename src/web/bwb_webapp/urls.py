from django.conf.urls import url
import django.contrib.auth.views
import django.views.generic
from django.urls import reverse_lazy

from . import views

urlpatterns = [
    url(r'^$', views.ChatListView.as_view(), name='index'),
    url(r'^expert/$', views.WatsonMarvelExpertView.as_view(), name='marvel_expert'),
    url(r'^chat/$', views.ChatListView.as_view(), name='chatOverview'),
    url(r'^chat/new/$', views.ChatCreateView.as_view(), name='chat_new'),
    url(r'^chat/(?P<pk>[0-9]+)/$', views.ChatDetailView.as_view(), name='chat'),
    url(r'^answer/$', views.QuestionAnswerPairsView.as_view(), name='question_answer_list'),
    url(r'^stats/$', views.StatsView.as_view(), name='stats'),
    url(r'^questionnaire/$', django.views.generic.TemplateView.as_view(template_name='bwb_webapp/questionnaire.html'), name='questionnaire'),

    url(r'^accounts/login/$', django.contrib.auth.views.login, {'template_name': 'bwb_webapp/login.html'}, name='login'),
    url(r'^accounts/register/$', views.RegistrationPageView.as_view(), name='register'),
    url(r'^accounts/logout/$', django.contrib.auth.views.logout, {'next_page': reverse_lazy('index')}, name='logout'),
]
