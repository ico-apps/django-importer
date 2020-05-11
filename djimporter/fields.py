import json
import time

from datetime import datetime

from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ObjectDoesNotExist, FieldError as dj_FieldError, ValidationError
from django.db.models import Manager
from django.db.models import Model as djangoModel
from django.db.models.query import QuerySet
from django.db.models import TimeField as django_TimeField


class FieldError(ValueError):
    pass


class ForeignKeyFieldError(FieldError):
    def __init__(self, msg, model, value):
        self.model = model
        self.value = value
        self.msg = msg
        super(ForeignKeyFieldError, self).__init__(self.msg)


class FieldValueMissing(FieldError):
    def __init__(self, field_name):
        super(FieldValueMissing, self).__init__("No value found for field %s" % field_name)


class ListGeoException(Exception):
    """
    Raised when no there are a field than it not is defined in the class
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class Field(object):
    position = 0
    field_name = "Field"
    # Are null values allowed?
    # If null value is allowed, this field could be empty in the row
    null = False

    def __init__(self, *args, **kwargs):
        self.in_csv = kwargs.pop('in_csv', True)

        if 'row_num' in kwargs:
            self.position = kwargs.pop('row_num')
        else:
            self.position = Field.position
            Field.position += 1
        if 'match' in kwargs:
            self.match = kwargs.pop('match')

        if 'null' in kwargs:
            self.null = kwargs.pop('null')

        if 'default' in kwargs:
            # with this value we can overwrite all values in csv
            # for this field. It is usefull when we can a default value
            # but we don't put one default value in the model
            self.has_default = self.to_python(kwargs.pop('default'))


class IntegerField(Field):
    field_name = "Integer"

    def to_python(self, value):
        if hasattr(self, "null") and not value:
            return None
        return int(value)


class TimeField(Field):
    field_name = "Time"

    def to_python(self, value):
        field = django_TimeField()
        return field.to_python(value)


class BooleanField(Field):
    field_name = "Boolean"

    def default_is_true_method(self, value):
        if hasattr(self, "null") and not value:
            return None
        return value.lower() == "true"


    def __init__(self, *args, **kwargs):
        if 'is_true' in kwargs:
            self.is_true_method = kwargs.pop('is_true')
        else:
            self.is_true_method = self.default_is_true_method
        super(BooleanField, self).__init__(*args, **kwargs)

    def to_python(self, value):
        return self.is_true_method(value)


class CharField(Field):
    field_name = "String"

    def to_python(self, value):
        if value:
            return value.strip()
        else:
            return value


class FloatField(Field):
    field_name = "Float"

    def to_python(self, value):
        return float(value)


class DateField(Field):
    field_name = "Date"

    def __init__(self, *args, **kwargs):
        strptime = '%Y-%m-%d %H:%M:%S'
        self.strptime = kwargs.pop('strptime', strptime)

    def to_python(self, value):
        if value:
            return datetime.strptime(value, self.strptime)
        else:
           return None


class IgnoredField(Field):
    field_name = "Ignore the value"

class ForeignKey(Field):
    field_name = "ForeignKey"

    def __init__(self, *args, **kwargs):
        self.pk = kwargs.pop('pk', 'pk')
        if len(args) < 1:
            raise ValueError("You should provide a Model as the first argument.")
        self.model = args[0]
        try:
            if not issubclass(self.model, djangoModel):
                raise TypeError("The first argument should be a django model class.")
        except TypeError as e:
            raise TypeError("The first argument should be a django model class.")
        super(ForeignKey, self).__init__(**kwargs)

    def to_python(self, value):
        try:
            return self.model.objects.get(**{self.pk: value})
        except ObjectDoesNotExist:
            msg = "No match found for %(model)s with value %(value)s"
            params = {'model': self.model.__name__, 'value': value}
            raise ValidationError(msg, params=params)


class SlugRelatedField(Field):
    # We use this field for match one object in one ForeignKey
    # but we need an other field that is not a tipical id
    # Practicaly is the same of ForeignKey but from other identificatior
    # not the id or pk
    field_name = "Slug_Related_Field"
    queryset = None

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.args = args
        self.kwargs = kwargs
        self.queryset = kwargs.pop('queryset', self.queryset)

        if 'match' in kwargs:
            self.match = kwargs['match']
        if 'slug_field' in kwargs:
            self.slug_field = kwargs['slug_field']

        assert self.queryset is not None, (
            'Relational field must provide a `queryset` argument, '
            'override `get_queryset`, or set read_only=`True`.'
        )
        self.model = self.queryset.model

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, (QuerySet, Manager)):
            # Ensure queryset is re-evaluated whenever used.
            # Note that actually a `Manager` class may also be used as the
            # queryset argument. This occurs on ModelSerializer fields,
            # as it allows us to generate a more expressive 'repr' output
            # for the field.
            # Eg: 'MyRelationship(queryset=ExampleModel.objects.all())'
            queryset = queryset.all()
        return queryset

    def get(self, value):
        # wee split in this function for help to RelatedFromUniquesField
        return self.get_queryset().get(**{self.slug_field: value.strip()})

    def to_python(self, value):
        # handle empty values depending of this field is mandatory
        if not value:
            if self.null:
                return None
            else:
                import pdb; pdb.set_trace()
                msg = 'This field cannot be empty'
                raise ValidationError(msg, code='required')

        try:
            return self.get(value)
        except ObjectDoesNotExist:
            msg = "No match found for %(model)s with value %(value)s"
            params = {'model': self.model.__name__, 'value': value}
            raise ValidationError(msg, params=params)
        except (TypeError, ValueError) as e:
            raise ValidationError(e, code='invalid')


class RelatedFromUniquesField(SlugRelatedField):
    # overwrite SlugRelatedField for du a query more complex
    # from fields of unique together

    field_name = "Related_Uniques_together_field"

    def get(self, dvalue):
        d = {k: dvalue[self.slug_field[k]].strip() for k in self.slug_field}
        return self.get_queryset().get(**d)


class SpeciesMappingField(SlugRelatedField):
    """
    overwrite SlugRelatedField for du a query more complex
    from SpeciesMappingCsv.
    Is not necessary save in the csvmodel becouse
    the to_python do this task

    """

    field_name = "SpeciesMappingField"

    def get(self, dvalue):
        d_source = self.slug_field['source']
        dict_source = {d_source[k].strip(): dvalue[k].strip()
                for k in d_source
        }
        d_dest = self.slug_field['dest']
        dict_dest = {d_dest[k].strip(): dvalue[k].strip()
                for k in d_dest
        }

        source = self.get_queryset().get(**dict_source)
        dest = self.get_queryset().get(**dict_dest)

        source.dst_species_mapping.add(dest)


class CsvRelated(Field):
    field_name = "Csv_Related"

    def __init__(self, *args, **kwargs):
        self.csvModel= args[0]

    def to_python(self, value):
        return value


class DefaultField(Field):
    """
    We use this field for override all values in csv or add one
    that not exist in the csv

    """

    field_name = "DefaultField"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.value = args[0]

    def to_python(self):
        return self.value


class ManyToManyField(Field):
    """
    We use this field for save one Information int csv in a
    additional table that to be a realtion many to many

    """

    field_name = "ManyToManyField"

    def __init__(self, *args, **kwargs):
        self.csvModel = args[0]
        self.method = self.csvModel.__name__.lower()
        if 'dict_params' in kwargs:
            self.dict_params = kwargs['dict_params']
        if 'match' in kwargs:
            self.match = kwargs['match']

    def task(self, object_father):
        if hasattr(object_father, self.method):
            method = getattr(object_father, self.method)
            getattr(method, 'add')(self.parameters)

    def to_python(self, colname, line_number, value):
        self.colname = colname
        self.line_number= line_number
        self.dict_params[self.match] = value

        p1 = self.csvModel.objects.get(**self.dict_params)
        self.parameters = p1
        return self


class CsvFieldLink(Field):
    """
    We use this field for save the same Information in to fields
    in the model but there are only one in the csv is offer.
    As args you get a dictionary composed for k the value in the
    model and v the column name from you want copy
    normaly this key not exist in the csv file.
    And is necessary that the name of the CsvFieldLink is the same
    than the key of this dictionary

    """

    field_name = "Csv_Field_Link"

    def __init__(self, *args, **kwargs):
        self.link = args[0]

    def to_python(self, value):
        return value


class ComposedKeyField(ForeignKey):
    def to_python(self, value):
        try:
            return self.model.objects.get(**value)
        except ObjectDoesNotExist as e:
            raise ForeignKeyFieldError("No match found for %s" % self.model.__name__, self.model.__name__, value)


class ListGeoField(Field):
    # We use this field insted of TaskField
    # becouse we want check the value before saved
    # the monitoring site
    field_name = "ListGeoField"

    def task(self, monitoring_site):
        # Task is a method used when the monitoring site is saved
        # The task pretend deserialized and saved the transects

        if hasattr(self, 'shape'):
            monitoring_site.deserialize_geojson(self.shape)

    def to_python(self, colname, line_number, value):
        self.colname = colname
        self.line_number= line_number

        null = False
        if hasattr(self, 'null'):
            null = self.null
        if not value:
            if not null:
                raise ListGeoException("ListGeo not exist")
            else:
                return self
        self.shape = json.loads(value)
        try:
            sections = [x['properties']['section'] for x in self.shape['features']]
        except KeyError as e:
            msg = "Malformed transect: %s" % e
            raise ValueError(msg)
        if len(sections) != len(set(sections)):
            msg = "There are sections duplicates sections: %s" % (tuple(sections),)
            raise ValueError(msg)

        return self


class TaskField(Field):
    """
    We use this field for diverse task that we want execute
    after one model is saved

    """

    field_name = "Task_Field"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.method = args[0]
        self.required = True
        self.f_args = ()
        self.parameters = ()
        if 'required' in kwargs:
            self.required = kwargs['required']
        if 'f_args' in kwargs:
            self.f_args = kwargs['f_args']


    def task(self, object_father):
        # we can execute one task next the object father is create
        # is like signal but we can du this next bulk_create
        if hasattr(object_father, self.method):
            if not self.in_csv:
                if self.parameters:
                    getattr(object_father, self.method)(*self.parameters)
                else:
                    getattr(object_father, self.method)()

            elif self.in_csv and self.parameters:
                    getattr(object_father, self.method)(*self.parameters)


    def to_python(self, colname, line_number, value):
        self.colname = colname
        self.line_number= line_number
        self.parameters = ()

        if not self.in_csv and self.f_args:
            self.parameters = self.f_args
        elif self.in_csv:
            if value:
                self.parameters = tuple(list(self.f_args)+[value])

            elif self.required and not value:
                raise FieldValueMissing(self.field_name)

            elif not self.required and not value:
                self.parameters = ()


        return self


class MultiSlugRelatedField(SlugRelatedField):
    """
    overwrite SlugRelatedField for do a query more complex
    from observation of pecbms.
    The target is get one value from more than one field of them.
    Is tipicaly when the foreingkey depend of more than one field.
    """

    field_name = "MultiSlugRelatedField"

    def __init__(self, *args, **kwargs):
        super(MultiSlugRelatedField, self).__init__(*args, **kwargs)
        # matchs is similar to match but is a dictionary
        # becouse is multiple
        self.matchs= kwargs.pop('matchs', None)

    def get(self, dvalue):
        return self.get_queryset().get(**dvalue)

    def to_python(self, line):
        try:
            dvalues = {self.matchs[k]: line[k].strip() for k in self.matchs.keys()}
            return self.get(dvalues)
        except ObjectDoesNotExist:
            raise ForeignKeyFieldError("No match found for %s" % self.model.__name__, self.model.__name__, line)
        except (TypeError, ValueError, KeyError):
            raise FieldError('invalid')
