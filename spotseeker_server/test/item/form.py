# Copyright 2024 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

from django.test import TestCase
from django.test.utils import override_settings
from spotseeker_server.forms.item import ItemForm, ItemExtendedInfoForm
from spotseeker_server.default_forms.item import DefaultItemForm,\
    DefaultItemExtendedInfoForm


DEFAULT_FORM = 'spotseeker_server.default_forms.item.DefaultItemForm'
DEFAULT_EI_FORM = ('spotseeker_server.default_forms.item.DefaultItem'
                   'ExtendedInfoForm')


@override_settings(
    SPOTSEEKER_AUTH_MODULE='spotseeker_server.auth.all_ok',
    SPOTSEEKER_SPOT_FORM=DEFAULT_FORM,
    SPOTSEEKER_SPOTEXTENDEDINFO_FORM=DEFAULT_EI_FORM)
class ItemFormsTest(TestCase):

    def test_default_item_form(self):
        """Ensure the loader grabs the right form"""
        form = ItemForm({})
        # Not using assertIsInstance because we want to check for an exact
        # match, not a subclass
        self.assertIs(type(form), DefaultItemForm)

    def test_valid_item(self):
        """Test validation for a valid item"""
        form_valid = ItemForm({
            'name': 'foo',
            'item_category': 'bar',
            'item_subcategory': 'baz',
        })
        self.assertTrue(form_valid.is_valid())

    def test_default_item_EI_form(self):
        """Ensure the loader grabs the right EI form"""
        eiform = ItemExtendedInfoForm({})
        self.assertIs(type(eiform), DefaultItemExtendedInfoForm)

    def test_valid_data(self):
        """Assert that valid data passes validation"""
        form_valid = ItemExtendedInfoForm(
            {'key': 'foo-bar_5', 'value': 'some_value'})
        self.assertTrue(form_valid.is_valid())

    def test_invalid_key(self):
        """Ensure a missing key causes validation to fail"""
        form_bad_key = ItemExtendedInfoForm(
            {'key': 'foo-bar_6+', 'value': 'other_value'})
        self.assertFalse(form_bad_key.is_valid())
        self.assertIn('key', form_bad_key.errors)
        self.assertIn('Key must be only', form_bad_key.errors['key'][0])

    def test_missing_value(self):
        """Ensure a missing value causes validation to fail"""
        form_no_value = ItemExtendedInfoForm({'key': 'valid_key'})
        self.assertFalse(form_no_value.is_valid())
        self.assertIn('value', form_no_value.errors)
        self.assertIn('This field is required.', form_no_value.errors['value'])

    def test_missing_key(self):
        """Ensure a missing key causes validation to fail"""
        form_no_key = ItemExtendedInfoForm({'value': 'valid_value'})
        self.assertFalse(form_no_key.is_valid())
        self.assertIn('key', form_no_key.errors)
        self.assertIn('This field is required.', form_no_key.errors['key'])
