from django import forms
from django.shortcuts import get_object_or_404
from django.utils.text import slugify
from text_unidecode import unidecode
from django.utils.translation import pgettext_lazy

from ...product.models import Category, Product, ProductClass


class CategoryForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.parent_pk = kwargs.pop('parent_pk')
        super(CategoryForm, self).__init__(*args, **kwargs)
        if self.instance.parent and self.instance.parent.hidden:
            self.fields['hidden'].widget.attrs['disabled'] = True
        for field_name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'

    class Meta:
        model = Category
        exclude = ['slug']

    def save(self, commit=True):
        self.instance.slug = slugify(unidecode(self.instance.name))
        if self.parent_pk:
            self.instance.parent = get_object_or_404(
                Category, pk=self.parent_pk)
        if self.instance.parent and self.instance.parent.hidden:
            self.instance.hidden = True
        super(CategoryForm, self).save(commit=commit)
        self.instance.set_hidden_descendants(self.cleaned_data['hidden'])
        return self.instance


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
        field.widget.attrs['class'] = 'form-control bootstrap-select'

        field = self.fields['available_on'] 
        field.widget.attrs['class'] = 'form-control pickadate-selectors'
         

        field = self.fields['name']
        field.widget.attrs['placeholder'] = pgettext_lazy(
            'Product form placeholder', 'Give your awesome product a name')
        field = self.fields['categories']        
        field.widget.attrs['data-placeholder'] = pgettext_lazy(
            'Product form placeholder', 'Search')
        field.widget.attrs['class'] = 'form-control multiselect'
        field.widget.attrs['multiple'] = 'multiple'         

        field = self.fields['product_tax']
        field.widget.attrs['class'] = 'form-control bootstrap-select'
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
                'initial': self.instance.get_attribute(attribute.pk)}
            
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


