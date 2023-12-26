from django.contrib import admin
from board.models import Comment, Post
# Register your models here.

#admin.site.register(Comment)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'post', 'content', 'create_dt', 'update_dt')
    
class CommentInline(admin.TabularInline):  # 또는 admin.StackedInline
    model = Comment
    extra = 1  # 추가적으로 표시될 Comment 폼의 수

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    inlines = [CommentInline]
    list_display = ("id","category","title","image","content","author","create_dt")