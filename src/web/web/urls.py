"""web URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from bwb_webapp.views import WelcomePageView
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from web import settings

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include('bwb_api.urls', namespace='api', app_name='api')),
    url(r'^app/', include('bwb_webapp.urls', namespace='app', app_name='app')),
    url(r'^$', WelcomePageView.as_view(), name='index'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
