"""Tests related to django_types.utils.DBType"""
from django.test import TestCase

from django_types.utils import DBType


class DBTypeTest(TestCase):
    def test_str(self):
        db_type = DBType('test_enum(%s, %s)', ['val1', 'val2'])
        expected = 'test_enum(val1, val2)'
        self.assertEqual(str(db_type), expected)

    def test_paramatized_no_params(self):
        db_type = DBType('test_enum', None)
        expected = ('test_enum', [])
        self.assertEqual(db_type.paramatized, expected)

    def test_paramatized_with_params(self):
        db_type = DBType('test_enum(%s, %s)', ['val1', 'val2'])
        expected = ('test_enum(%s, %s)', ['val1', 'val2'])
        self.assertEqual(db_type.paramatized, expected)

    def test_paramatized_no_params_reuse(self):
        """
        Tests that the parameters used by DBType without any parameters are not reused between instances.

        Reusing the params instance causes problem during migration execution, as the BaseDatabaseSchemaEditor
        adds default values to the parameters list.
        """
        db_type_1 = DBType('enum_1')
        db_type_2 = DBType('enum_2')
        paramatized_1 = db_type_1.paramatized
        paramatized_2 = db_type_2.paramatized
        self.assertFalse(paramatized_1[1] is paramatized_2[1])
