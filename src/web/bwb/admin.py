from bwb.models import Chat, Message, WatsonMessage, KBFact, KBEntity, KBFactType, KBFactTypePattern, ChatRecentFunFact, \
    WatsonProcessingLogEntry
from django.contrib import admin


@admin.register(Chat)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'active', 'start_timestamp')


@admin.register(Message)
class PostAdmin(admin.ModelAdmin):
    list_display = ('creation_timestamp', 'author', 'text_excerpt', 'chat')
    list_display_links = ['creation_timestamp']
    list_filter = ['author', 'chat']


@admin.register(WatsonMessage)
class WatsonMessageAdmin(admin.ModelAdmin):
    list_display = ('creation_timestamp', 'text', 'chat', 'answerable')
    list_display_links = ['creation_timestamp']
    list_filter = ['chat']


@admin.register(WatsonProcessingLogEntry)
class WatsonProcessingLogEntryAdmin(admin.ModelAdmin):
    list_display = ['creation_timestamp', 'chat', 'requesting_message', 'exception_occurred']
    list_display_links = ['creation_timestamp']
    list_filter = ['chat']


@admin.register(KBFact)
class KBFactAdmin(admin.ModelAdmin):
    list_display = ('pk', 'type', 'source_id', 'definition')
    list_display_links = ['pk']
    list_filter = ['type']
    search_fields = ['source_id', 'definition']


@admin.register(KBEntity)
class KBEntityAdmin(admin.ModelAdmin):
    list_display = ['name', 'fact']
    list_display_links = ['name']


@admin.register(KBFactType)
class KBFactTypeAdmin(admin.ModelAdmin):
    list_display = ['name']
    list_display_links = ['name']


@admin.register(KBFactTypePattern)
class KBFactTypeSentenceAdmin(admin.ModelAdmin):
    list_display = ['name', 'fact_type', 'template_text']
    list_display_links = ['name']
    list_filter = ['fact_type']


@admin.register(ChatRecentFunFact)
class ChatRecentFunFactAdmin(admin.ModelAdmin):
    list_display = ['creation_timestamp', 'chat', 'fact', 'pattern']
    list_display_links = ['creation_timestamp']
    list_filter = ['chat', 'fact', 'pattern']
