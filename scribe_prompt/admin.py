from django.contrib import admin

from .models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    # Columns displayed in the main admin table list
    list_display = ('username', 'rating', 'comments', 'created_at')

    # Adds a clickable filtering column sidebar on the right
    list_filter = ('rating', 'created_at')

    # Adds a top search bar matching database text columns
    search_fields = ('username',)

    # Dynamically makes every field in the model read-only
    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    # Prevent users from adding new entries via the admin panel
    def has_add_permission(self, request):
        return False

    # Prevent users from deleting entries via the admin panel
    def has_delete_permission(self, request):
        return False
