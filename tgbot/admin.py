from django.contrib import admin

from tgbot.models import Member, Chat, Room, RoomMember


@admin.register(Chat)
class ChatAdmin(admin.ModelAdmin):
    pass

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    pass

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    pass

@admin.register(RoomMember)
class RoomMemberAdmin(admin.ModelAdmin):
    pass
