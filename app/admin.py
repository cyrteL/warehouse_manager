# app/admin.py
from django.contrib import admin

from .models import (
    Category, Housing, Location, PrivateAccount,
    Project, Room, Supplier, Ware, WarePhoto,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}   # slug генерируется из name прямо в форме, вручную вводить не надо


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(PrivateAccount)
class PrivateAccountAdmin(admin.ModelAdmin):
    list_display = ('account',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'account')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Housing)
class HousingAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'housing')
    list_filter = ('housing',)   # без этого при десятках комнат в разных корпусах список неудобно листать


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('name', 'room')
    list_filter = ('room__housing', 'room')


class WarePhotoInline(admin.TabularInline):
    """Фото редактируются прямо на странице изделия, не отдельным списком — меньше кликов при вводе."""
    model = WarePhoto
    extra = 1


@admin.register(Ware)
class WareAdmin(admin.ModelAdmin):
    list_display = ('name', 'inventory', 'status', 'category', 'project', 'location', 'quantity')
    list_filter = ('status', 'category', 'project')   # это то, что реально пригодится при 300+ изделиях из описи
    search_fields = ('name', 'inventory', 'serial')     # без этого искать конкретное изделие среди сотен — вручную листать
    inlines = [WarePhotoInline]