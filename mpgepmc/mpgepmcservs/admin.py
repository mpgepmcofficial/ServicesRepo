from django.contrib import admin
from .models import ServiceClass, Service, Package, PackageFeature, PaymentMethod, Order

# --- Inlines for Nested Management ---

class PackageFeatureInline(admin.TabularInline):
    model = PackageFeature
    extra = 1

class PackageInline(admin.StackedInline):
    model = Package
    extra = 1
    show_change_link = True
    fields = ('package_type', ('duration_value', 'duration_unit'), ('min_price_usd', 'max_price_usd'), 'button_type', 'is_active')

    def get_inlines(self, request, obj=None):
        """Allow features to be managed only when creating/editing a package directly, not via ServiceInline."""
        return []

@admin.register(Package)
class PackageAdmin(admin.ModelAdmin):
    list_display = ('package_type', 'service', 'duration_value', 'duration_unit', 'get_display_price', 'button_type', 'is_active')
    list_filter = ('service__service_class', 'service', 'duration_unit', 'button_type', 'is_active')
    search_fields = ('package_type', 'service__name')
    inlines = [PackageFeatureInline]
    readonly_fields = ('get_display_price',)

    def get_display_price(self, obj):
        return obj.get_display_price()
    get_display_price.short_description = 'Price Range (USD)'

class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1
    fields = ('name', 'short_description')
    show_change_link = True

@admin.register(ServiceClass)
class ServiceClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'slug')
    inlines = [ServiceInline]
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'service_class', 'short_description')
    list_filter = ('service_class',)
    prepopulated_fields = {'slug': ('name',)}
    inlines = [PackageInline]

# --- Other Models ---

@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_enabled', 'is_visible', 'sort_order')
    list_editable = ('is_enabled', 'is_visible', 'sort_order')
    
    # Pre-populate initial data for the user in the shell or via fixtures

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'total_amount', 'created_at', 'session_key')
    list_filter = ('created_at',)
    readonly_fields = ('session_key', 'total_amount', 'created_at')
