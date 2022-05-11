from django.contrib import admin
from product.models import Category, Product, Images, Brand, Size, Color, \
    Variants,Comment, Ip, Slider, Stock, ProductLangEN, CategoryLangEn
from django import forms
import admin_thumbnails
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from mptt.admin import DraggableMPTTAdmin




class NewsAdminForm(forms.ModelForm):
    detail = forms.CharField(widget=CKEditorUploadingWidget())

    class Meta:
        model = Product
        fields = '__all__'


class CategoryLangENInline(admin.TabularInline):
    model = CategoryLangEn
    extra = 1
    show_change_link = True
    prepopulated_fields = {'slug': ('title',)}



class CategoryAdmin2(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)
    inlines = [CategoryLangENInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)


        qs = Category.objects.add_related_count(
                qs,
                Product,
                'category',
                'products_cumulative_count',
                cumulative=True)


        qs = Category.objects.add_related_count(qs,
                 Product,
                 'category',
                 'products_count',
                 cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count
    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count
    related_products_cumulative_count.short_description = 'Related products (in tree)'


class CategoryAdmin3(DraggableMPTTAdmin):
    mptt_indent_field = "title"
    list_display = ('tree_actions', 'indented_title',
                    'related_products_count', 'related_products_cumulative_count')
    list_display_links = ('indented_title',)


    def get_queryset(self, request):
        qs = super().get_queryset(request)


        qs = CategoryLangEn.objects.add_related_count(
                qs,
                Product,
                'category',
                'products_cumulative_count',
                cumulative=True)


        qs = CategoryLangEn.objects.add_related_count(qs,
                 Product,
                 'category',
                 'products_count',
                 cumulative=False)
        return qs

    def related_products_count(self, instance):
        return instance.products_count
    related_products_count.short_description = 'Related products (for this specific category)'

    def related_products_cumulative_count(self, instance):
        return instance.products_cumulative_count
    related_products_cumulative_count.short_description = 'Related products (in tree)'


@admin_thumbnails.thumbnail('image')
class ProductImageInline(admin.TabularInline):
    model = Images
    readonly_fields = ('id',)
    extra = 1


@admin_thumbnails.thumbnail('image')
class ImagesAdmin(admin.ModelAdmin):
    list_display = ['image','title','image_thumbnail']





class ProductLangENInline(admin.TabularInline):
    model = ProductLangEN
    extra = 1
    show_change_link = True
    prepopulated_fields = {'slug': ('title',)}


class StockLine(admin.TabularInline):
    model = Stock
    extra = 1
    show_change_link = True


class VariantsLine(admin.TabularInline):
    model = Variants
    extra = 1
    show_change_link = True


class ProductAdmin(admin.ModelAdmin):
    form = NewsAdminForm
    list_display = ['title']
    list_filter = ['category']
    inlines = [ProductImageInline, ProductLangENInline, StockLine, VariantsLine]
    prepopulated_fields = {'slug': ('title',)}




class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('title',)}


admin.site.register(Category, CategoryAdmin2)
admin.site.register(Product, ProductAdmin)
admin.site.register(Variants)
admin.site.register(Brand, BrandAdmin)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Comment)
admin.site.register(Ip)
admin.site.register(Slider)
admin.site.register(Stock)
admin.site.register(ProductLangEN)
admin.site.register(CategoryLangEn, CategoryAdmin3)