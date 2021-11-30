"""
The `CsvModel` class is essentially shortcuts for automatically creating
serializers based on a given model class.
These tests deal with ensuring that we correctly map the model fields onto
an appropriate set of serializer fields for each case.
"""
import os

from django.core.exceptions import ValidationError
from django.test import TestCase

from djimporter import fields, importers

from .models import ForeignKeySource, ForeignKeyTarget, Musician, Album

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

TESTDATA_DIR = os.path.join(BASE_DIR, 'data/')


class SlugFieldMapping(TestCase):
    def test_valid(self):
        Musician.objects.bulk_create([
            Musician(name="Susan Schmith", instrument="guitar"),
            Musician(name="Johan Wolf", instrument="piano"),
        ])

        class AlbumCsv(importers.CsvModel):
            artist = fields.SlugRelatedField(slug_field="name", queryset=Musician.objects.all())

            class Meta:
                delimiter = ';'
                dbModel = Album
                fields = ['name', 'release_date', 'num_stars', 'artist']

        csv_path = os.path.join(TESTDATA_DIR, 'albums.csv')
        importer = AlbumCsv(csv_path)

        self.assertTrue(importer.is_valid())

    def test_missing_slug_related(self):
        class ForeignKeySourceCsv(importers.CsvModel):
            target = fields.SlugRelatedField(
                queryset=ForeignKeyTarget.objects.all(), slug_field='name')

            class Meta:
                dbModel = ForeignKeySource
                fields = ('name', 'target')

        ForeignKeyTarget.objects.create(name='bar')

        csv_path = os.path.join(TESTDATA_DIR, 'ForeignKeySource.csv')
        importer = ForeignKeySourceCsv(csv_path)

        self.assertFalse(importer.is_valid())


class CachedSlugFieldTest(TestCase):
    def test_valid(self):
        ForeignKeyTarget.objects.bulk_create([
            ForeignKeyTarget(name='bar'),
            ForeignKeyTarget(name='bar2'),
        ])

        class ForeignKeySourceCsv(importers.CsvModel):
            target = fields.CachedSlugRelatedField(
                queryset=ForeignKeyTarget.objects.all(), slug_field='name')

            class Meta:
                dbModel = ForeignKeySource
                fields = ('name', 'target')

        csv_path = os.path.join(TESTDATA_DIR, 'ForeignKeySource_valid.csv')
        importer = ForeignKeySourceCsv(csv_path)

        self.assertTrue(importer.is_valid(), importer.errors)

    def test_invalid_missing_required_target_value(self):
        ForeignKeyTarget.objects.create(name='bar')

        class ForeignKeySourceCsv(importers.CsvModel):
            target = fields.CachedSlugRelatedField(
                queryset=ForeignKeyTarget.objects.all(), slug_field='name')

            class Meta:
                dbModel = ForeignKeySource
                fields = ('name', 'target')

        csv_path = os.path.join(TESTDATA_DIR, 'ForeignKeySource.csv')
        importer = ForeignKeySourceCsv(csv_path)

        self.assertFalse(importer.is_valid())


class DateFieldTest(TestCase):
    def test_unexpected_date_format(self):
        created = fields.DateField()
        self.assertRaises(ValidationError, created.to_python, '19/04/02 07:50')


class IntegerField(TestCase):
    def test_invalid_literal(self):
        count = fields.IntegerField()
        self.assertRaises(ValidationError, count.to_python, 'U')


class TimeFieldTest(TestCase):
    def test_allow_null_values(self):
        start_time = fields.TimeField(null=True)
        self.assertIsNone(start_time.to_python(''))

    def test_explicit_disallow_null_values(self):
        start_time = fields.TimeField(null=False)
        self.assertRaises(ValidationError, start_time.to_python, '')
