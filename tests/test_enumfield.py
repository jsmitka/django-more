""" Run tests related to django_enum.EnumField """
# Framework imports
from django.db.models.fields import BLANK_CHOICE_DASH
from django_enum import EnumField
from .models import TestEnum, WrongEnum, MetaEnum
from . import FieldTestCase


class EnumFieldTest(FieldTestCase):
    multi_db = True

    def test_create(self):
        field = EnumField(TestEnum)

        self.assertEqual(field.type_def, TestEnum)

    def test_assignment(self):
        self.assertFieldValue(
            fieldclass=EnumField,
            valid={
                'The first value': TestEnum.VAL1,
                'The second value': TestEnum.VAL2,
                'Third value is the best': TestEnum.VAL3,
                TestEnum.VAL1: TestEnum.VAL1,
                TestEnum.VAL2: TestEnum.VAL2,
                TestEnum.VAL3: TestEnum.VAL3},
            invalid={
                'The invalid value': 'not in enumeration',
                'VAL1': 'not in enumeration',
                'VAL2': 'not in enumeration',
                '': 'not in enumeration',
                'None':  'not in enumeration',
                WrongEnum.VAL1: 'incompatible enumeration',
                WrongEnum.VAL3: 'incompatible enumeration',
                1: 'not an enum member or string',
                -5:  'not an enum member or string',
                123: 'not an enum member or string',
                (): 'not an enum member or string',
                None: 'cannot be null'},
            field_args=[TestEnum])

    def test_meta_not_member(self):
        self.assertEqual(
            dict(MetaEnum.__members__),
            {
                'VAL1': MetaEnum.VAL1,
                'VAL2': MetaEnum.VAL2,
                'VAL3': MetaEnum.VAL3
            })

    def test_case_insensitive(self):
        self.assertFieldValue(
            fieldclass=EnumField,
            valid={
                'THE FIRST VALUE': TestEnum.VAL1,
                'the second value': TestEnum.VAL2,
                'ThirD vaLue IS the bEst': TestEnum.VAL3},
            invalid={
                'The invalid value': 'not in enumeration',
                123: 'not an enum member or string',
                WrongEnum.VAL1: 'incompatible enumeration',
                WrongEnum.VAL3: 'incompatible enumeration'},
            field_args=[TestEnum],
            field_kwargs={'case_sensitive': False})

    def test_default_choices(self):
        field = EnumField(TestEnum)
        choices = field.get_choices(blank_choice=BLANK_CHOICE_DASH)
        expected = BLANK_CHOICE_DASH + [(str(em), em.value) for em in TestEnum]
        self.assertEqual(choices, expected)

    def test_manual_choices(self):
        members = [TestEnum.VAL1, TestEnum.VAL2]
        field = EnumField(TestEnum, choices=members)
        choices = field.get_choices(blank_choice=BLANK_CHOICE_DASH)
        expected = BLANK_CHOICE_DASH + [(str(em), em.value) for em in members]
        self.assertEqual(choices, expected)

    def test_default_stringify(self):
        """
        Tests that the default value is converted to string when an Enum member is passed as the default.
        """
        field = EnumField(TestEnum, default=TestEnum.VAL2)
        self.assertEqual(field.default, TestEnum.VAL2.value)

    def test_clone_default(self):
        """
        Tests that the default value is not lost when cloning the field.
        """
        field = EnumField(TestEnum, default=TestEnum.VAL2.value)
        cloned_field = field.clone()
        self.assertEqual(cloned_field.default, TestEnum.VAL2.value)

    def test_clone_choices(self):
        """
        Tests that the choices list is not lost when cloning the field.
        """
        members = [TestEnum.VAL1, TestEnum.VAL2]
        field = EnumField(TestEnum, choices=members)
        cloned_field = field.clone()
        expected = [(str(em), em.value) for em in members]
        self.assertEqual(cloned_field.choices, expected)

    def test_deconstruct_manual_choices_without_enum(self):
        """
        Tests that the choices list is not lost when deconstructing a field that is not bound to an enum. This occurs
        when the schema is reconstructed from migrations and losing the value might cause the field to be marked
        as updated even when there is no change.
        """
        choices_list = [('VAL1', 'Value 1'), ('VAL2', 'Value 2')]
        field = EnumField(choices=choices_list)
        name, path, args, kwargs = field.deconstruct()
        expected_kwargs = {'choices': choices_list}
        self.assertEqual(kwargs, expected_kwargs)

    def test_clone_type_def(self):
        """
        Tests that the type def field is cloned properly when cloning the field.
        """
        field = EnumField(TestEnum)
        cloned_field = field.clone()
        self.assertEqual(cloned_field.type_def, TestEnum)
