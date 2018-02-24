from __future__ import unicode_literals

from django import forms
from django.db import transaction
from django.db.models import Count
from django.forms.models import ModelChoiceIterator, inlineformset_factory
from django.utils.encoding import smart_text
from django.utils.text import slugify
from django.utils.translation import pgettext_lazy

from ...product.models import (AttributeChoiceValue, Product, ProductAttribute,
                               ProductClass, ProductImage, ProductVariant,
                               Stock, StockLocation, VariantImage, ProductTax)
from .widgets import ImagePreviewWidget
from ...search import index as search_index


# purchase forms
class StockPurchaseForm(forms.ModelForm):
    class Meta:
        model = Stock
        exclude = ['quantity_allocated']


class ProductTaxForm(forms.ModelForm):
    class Meta:
        model = ProductTax
        exclude = []

    def __init__(self, *args, **kwargs):        
        super(ProductTaxForm, self).__init__(*args, **kwargs)     
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class ProductClassSelectorForm(forms.Form):
    MAX_RADIO_SELECT_ITEMS = 5

    def __init__(self, *args, **kwargs):
        product_classes = kwargs.pop('product_classes', [])
        super(ProductClassSelectorForm, self).__init__(*args, **kwargs)
        choices = [(obj.pk, obj.name) for obj in product_classes]
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control select'
        if len(product_classes) > self.MAX_RADIO_SELECT_ITEMS:
            widget = forms.Select
        else:
            widget = forms.RadioSelect
        self.fields['product_cls'] = forms.ChoiceField(
            label=pgettext_lazy('Product class form label', 'Product type'),
            choices=choices, widget=widget)
        field = self.fields['product_cls'] 
        field.widget.attrs['class'] = 'form-control select'


class StockForm(forms.ModelForm):
    class Meta:
        model = Stock
        exclude = ['quantity_allocated']

    def __init__(self, *args, **kwargs):
        product = kwargs.pop('product')
        super(StockForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        if not product.product_class.has_variants:
            initial = product.variants.first()
        else:
            initial = None

        self.fields['variant'] = forms.ModelChoiceField(
            queryset=product.variants, initial=initial)
        field = self.fields['variant'] 
        field.widget.attrs['class'] = 'form-control select-variant'

        field = self.fields['location'] 
        field.widget.attrs['class'] = 'form-control select'


class ProductClassForm(forms.ModelForm):
    class Meta:
        model = ProductClass
        exclude = []
        labels = {
            'variant_attributes': pgettext_lazy(
                'Product class form label',
                'Variants'),
            'product_attributes': pgettext_lazy(
                'Product class form label',
                'Attributes')}

    def __init__(self, *args, **kwargs):       
        super(ProductClassForm, self).__init__(*args, **kwargs)
        field = self.fields['product_attributes'] 
        field.widget.attrs['class'] = 'form-control multiselect'
        field.widget.attrs['multiple'] = 'multiple'

        field = self.fields['name'] 
        field.widget.attrs['class'] = 'form-control'

        field = self.fields['is_shipping_required'] 
        field.widget.attrs['class'] = 'form-styled'

        field = self.fields['has_variants'] 
        field.widget.attrs['class'] = 'form-styled'
        
        
        field = self.fields['variant_attributes'] 
        field.widget.attrs['class'] = 'form-control multiselect'
        field.widget.attrs['multiple'] = 'multiple'

    def clean(self):
        data = super(ProductClassForm, self).clean()
        product_attr = set(self.cleaned_data['product_attributes'])
        variant_attr = set(self.cleaned_data['variant_attributes'])
        has_variants = self.cleaned_data['has_variants']
        if not has_variants and len(variant_attr) > 0:
            msg = pgettext_lazy(
                'Product class form error',
                'Product variants are disabled.')
            self.add_error('variant_attributes', msg)
        # if len(product_attr & variant_attr) > 0:
        if len(product_attr & variant_attr) > 0:
            msg = pgettext_lazy(
                'Product class form error',
                'A single attribute can\'t belong to both a product '
                'and its variant.')
            self.add_error('variant_attributes', msg)

        if self.instance.pk:
            variants_changed = not (self.fields['has_variants'].initial ==
                                    has_variants)
            if variants_changed:
                query = self.instance.products.all()
                query = query.annotate(variants_counter=Count('variants'))
                query = query.filter(variants_counter__gt=1)
                if query.exists():
                    msg = pgettext_lazy(
                        'Product class form error',
                        'Some products of this type have more than '
                        'one variant.')
                    self.add_error('has_variants', msg)
        return data


class ProductForm(forms.ModelForm):

    class Meta:
        model = Product
        exclude = ['attributes']

    def __init__(self, *args, **kwargs):
        self.product_attributes = []
        super(ProductForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

        field = self.fields['is_featured'] 
        field.widget.attrs['class'] = 'styled' 

        field = self.fields['product_class']
        field.widget.attrs['class'] = 'form-control bootstrap-select input-group-btn'
        field.widget.attrs['data-live-search'] = 'true'
        field.widget.attrs['data-width'] = '100%'
        field.widget.attrs['tabindex'] = '-98'

        field = self.fields['product_supplier'] 
        field.widget.attrs['class'] = 'form-control bootstrap-select input-group-btn'
        field.widget.attrs['data-live-search'] = 'true'
        field.widget.attrs['data-width'] = '100%'
        field.widget.attrs['tabindex'] = '-98'       
        
        field = self.fields['available_on'] 
        field.widget.attrs['class'] = 'form-control pickadate-selectors'
         

        field = self.fields['name']
        field.widget.attrs['placeholder'] = pgettext_lazy(
            'Product form placeholder', 'Give your awesome product a name')

        field = self.fields['categories']
        field.widget.attrs['data-placeholder'] = pgettext_lazy(
            'Product form placeholder', 'Select')
        field.widget.attrs['class'] = 'form-control '
        field.widget.attrs['style'] = 'display:none;'         

        field = self.fields['product_tax']
        field.widget.attrs['class'] = 'form-control bootstrap-select'
        field.widget.attrs['data-live-search'] = 'true'
        product_class = self.instance.product_class
        self.product_attributes = product_class.product_attributes.all()
        self.product_attributes = self.product_attributes.prefetch_related(
            'values')
        self.prepare_fields_for_attributes()

    def prepare_fields_for_attributes(self):
        for attribute in self.product_attributes:            
            field_defaults = {               
                'label': attribute.name,
                'required': False,
                'initial': self.instance.get_attribute(attribute.pk),}
            if attribute.has_values():
                field = CachingModelChoiceField(
                    queryset=attribute.values.all(), **field_defaults)
                field.widget.attrs['class'] = 'form-control select'
            else:
                field = forms.CharField(**field_defaults)
                field.widget.attrs['class'] = 'form-control'
            self.fields[attribute.get_formfield_name()] = field
            
    def iter_attribute_fields(self):
        for attr in self.product_attributes:
            yield self[attr.get_formfield_name()]

    def save(self, commit=True):
        attributes = {}
        for attr in self.product_attributes:
            value = self.cleaned_data.pop(attr.get_formfield_name())
            if isinstance(value, AttributeChoiceValue):
                attributes[smart_text(attr.pk)] = smart_text(value.pk)
            else:
                attributes[smart_text(attr.pk)] = value
        self.instance.attributes = attributes
        instance = super(ProductForm, self).save(commit=commit)
        search_index.insert_or_update_object(instance)
        return instance


class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        exclude = ['attributes', 'product', 'images']

    def __init__(self, *args, **kwargs):
        super(ProductVariantForm, self).__init__(*args, **kwargs)
        if self.instance.product.pk:
            self.fields['variant_supplier'].widget.attrs[
                'data-live-search'] = 'true'
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class CachingModelChoiceIterator(ModelChoiceIterator):
    def __iter__(self):
        if self.field.empty_label is not None:
            yield ('', self.field.empty_label)
        for obj in self.queryset:
            yield self.choice(obj)


class CachingModelChoiceField(forms.ModelChoiceField):
    def _get_choices(self):
        if hasattr(self, '_choices'):
            return self._choices
        return CachingModelChoiceIterator(self)
    choices = property(_get_choices, forms.ChoiceField._set_choices)


class VariantAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = []

    def __init__(self, *args, **kwargs):
        super(VariantAttributeForm, self).__init__(*args, **kwargs)
        attrs = self.instance.product.product_class.variant_attributes.all()
        self.available_attrs = attrs.prefetch_related('values')
        ats = []
        for attr in self.available_attrs:
            ats.append(attr.pk)
            field_defaults = {'label': attr.name,
                              'required': True,
                              'initial': self.instance.get_attribute(attr.pk)}
            if attr.has_values():
                field = CachingModelChoiceField(
                    queryset=attr.values.all(), **field_defaults)
            else:
                field = forms.CharField(**field_defaults)
            self.fields[attr.get_formfield_name()] = field
        i = 0
        for field_name, field in self.fields.items():            
            field.widget.attrs['class'] = 'form-control bootstrap-select dynamicxedit'
            field.widget.attrs['data-live-search'] = 'true'
            field.widget.attrs['data-pk'] = ats[i]
            i+=1

    def save(self, commit=True):
        attributes = {}
        for attr in self.available_attrs:
            value = self.cleaned_data.pop(attr.get_formfield_name())
            if isinstance(value, AttributeChoiceValue):
                attributes[smart_text(attr.pk)] = smart_text(value.pk)
            else:
                attributes[smart_text(attr.pk)] = value
        self.instance.attributes = attributes
        return super(VariantAttributeForm, self).save(commit=commit)


class VariantBulkDeleteForm(forms.Form):
    items = forms.ModelMultipleChoiceField(queryset=ProductVariant.objects)

    def delete(self):
        items = ProductVariant.objects.filter(
            pk__in=self.cleaned_data['items'])
        items.delete()


class StockBulkDeleteForm(forms.Form):
    items = forms.ModelMultipleChoiceField(queryset=Stock.objects)

    def delete(self):
        items = Stock.objects.filter(pk__in=self.cleaned_data['items'])
        items.delete()


class ProductImageForm(forms.ModelForm):
    variants = forms.ModelMultipleChoiceField(
        queryset=ProductVariant.objects.none(),
        widget=forms.CheckboxSelectMultiple, required=False)

    class Meta:
        model = ProductImage
        exclude = ('product', 'order')

    def __init__(self, *args, **kwargs):
        super(ProductImageForm, self).__init__(*args, **kwargs)
        show_variants = self.instance.product.product_class.has_variants
        if self.instance.product and show_variants:
            variants = self.fields['variants']
            variants.queryset = self.instance.product.variants.all()
            variants.initial = self.instance.variant_images.values_list(
                'variant', flat=True)
        if self.instance.image:
            field = self.fields['image']
            field.widget.attrs['class'] = 'file-styled'
        field = self.fields['alt'] 
        field.widget.attrs['class'] = 'form-control'

        field = self.fields['variants']
        field.widget.attrs['class'] = 'styled'


    @transaction.atomic
    def save_variant_images(self, instance):
        variant_images = []
        # Clean up old mapping
        instance.variant_images.all().delete()
        for variant in self.cleaned_data['variants']:
            variant_images.append(
                VariantImage(variant=variant, image=instance))
        VariantImage.objects.bulk_create(variant_images)

    def save(self, commit=True):
        instance = super(ProductImageForm, self).save(commit=commit)
        self.save_variant_images(instance)
        return instance


class ProductAttributeForm(forms.ModelForm):
    class Meta:
        model = ProductAttribute
        exclude = []
    def __init__(self, *args, **kwargs):
        self.product_attributes = []
        super(ProductAttributeForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class StockLocationForm(forms.ModelForm):
    class Meta:
        model = StockLocation
        exclude = []
    def __init__(self, *args, **kwargs):        
        super(StockLocationForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


class AttributeChoiceValueForm(forms.ModelForm):
    class Meta:
        model = AttributeChoiceValue
        exclude = ('slug','color')
    def __init__(self, *args, **kwargs):        
        super(AttributeChoiceValueForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'


    def save(self, commit=True):
        self.instance.slug = slugify(self.instance.name)
        return super(AttributeChoiceValueForm, self).save(commit=commit)



AttributeChoiceValueFormset = inlineformset_factory(
    ProductAttribute, AttributeChoiceValue, form=AttributeChoiceValueForm,
    extra=1)
