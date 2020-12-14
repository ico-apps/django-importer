"""
Define the csv model base classe
"""
import csv
import io
import os

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, transaction
from django.utils.translation import gettext as _


class MetaFieldException(Exception):
    """
    Raised when no there are a field than it not is defined in the class
    """
    def __init__(self, message):
        Exception.__init__(self, message)


class CsvModel(object):

    def __init__(self, csvfile, context=None):
        self.file = csvfile
        self.context = context or {}
        self.Meta.context = context

        self.errors = []
        self.list_tasks = []
        self.list_objs = []
        self.dict_error = {}
        self._meta = None

        self.fields = self.get_fields()
        self.extra_fields = getattr(self.Meta, 'extra_fields', [])
        self.mapping = self.get_mapping()
        self.delimiter = getattr(self.Meta, 'delimiter', ';')
        self.dbModel = self.Meta.dbModel
        self.post_save = hasattr(self.Meta, 'post_save')
        self.has_save = hasattr(self.Meta, 'save') and self.Meta.save
        self.not_create_model = hasattr(self.Meta, 'create_model') and not self.Meta.create_model

    def get_user_visible_fields(self):
        # extra fields is used to capture the names of the columns used in the pre_save and
        # post_save methods each csvmodel. Is neccesary define in every Meta of csvmodel one list
        # of this names if is used in pre_save or post_save
        # This method get_user_visible_fields is used for validated the header of the file
        head = self.extra_fields.copy()
        for f in self.mapping.keys():
            field = self.fields[f]
            if hasattr(field, 'in_csv') and not field.in_csv:
                continue

            if f in self.context:
                continue

            head.append(f)

        return head

    def get_fields(self):
        """
        Only get the names than exist in the field
        if not exist names enough for build the object
        when the it try validate the object to do crash
        """
        if hasattr(self, 'fields'):
            return self.fields

        attributes = {}
        dbModel = self.Meta.dbModel
        dmodel = {a.name: a for a in dbModel._meta.get_fields()}
        # Get all fields than is defined in the class
        for f in self.Meta.fields:
            if hasattr(self, f):
                attributes[f] = getattr(self, f)
            else:
                attributes[f] = dmodel[f]

        return attributes

    def get_mapping(self):
        """
        The mapping consist in a dictionary when the keys is
        the names of the columns and the value is the names
        of the fields of the model
        """
        match = {}
        for k, v in self.get_fields().items():
            if hasattr(v, 'match'):
                match[k] = v.match
            else:
                match[k] = k

        return match

    def add_error(self, line, field, error):
        err_dict = {'line': line,
                    'error': {field: error}
                    }
        self.errors.append(err_dict)

    def get_dict_error(self):
        if self.dict_error:
            return self.dict_error

        msg = _("the head field '%s' not do match")
        self.dict_error = {i: (msg % i) for i in self.get_user_visible_fields()}
        return self.dict_error

    def open_file(self, path):
        txt = open(path).read()
        csv = bytes(txt, encoding='utf-8')
        return io.BytesIO(csv)

    def is_valid(self):
        csv_file = self.file
        if isinstance(self.file, str):
            csv_file = self.open_file(self.file)
        self.csv_file = csv_file.read().decode('UTF-8').splitlines()
        self.csv_reader = csv.DictReader(self.csv_file, delimiter=self.delimiter)
        self.validate_header()
        if self.errors:
            return False

        for line_number, line in enumerate(self.csv_reader, start=2):
            # line is a dictionary with the fields of csv head as key
            # and values of the row as value of the dictionary
            self.process_line(line, line_number)

        self.validate_in_file()
        if self.errors:
            if self.has_save:
                # delete related objects created if there are errors
                # while processing post_save operations
                ids = [o.object.id for o in self.list_objs]
                self.dbModel.objects.filter(id__in=ids).delete()
            return False

        return True

    def validate_header(self):
        if self.errors: return False

        errors = {}
        for f in self.get_user_visible_fields():
            if f not in self.csv_reader.fieldnames:
                errors.update({f: _(self.get_dict_error()[f])})

        if errors:
            self.add_error(1, 'header', errors)
            return False
        return True

    def save(self):
        if self.errors: return self.errors
        if self.has_save: return
        if self.not_create_model: return

        lines = []
        for i in self.list_objs:
            if i.object:
                lines.append(i.object)
            else:
                continue

        try:
            with transaction.atomic():
                self.dbModel.objects.bulk_create(lines, batch_size=20)

                if not self.post_save: return
                for row in self.list_objs:
                    row.post_save()
                    if row.errors:
                        self.errors.extend(row.errors)

        except DatabaseError as e:
            self.add_error(1, "Error Database", {"Error Database": e.args})

    def process_line(self, line, line_number):
        data = {
            'line': line,
            'line_number': line_number,
            'context': self.context,
            'meta': self.Meta,
            'fields': self.fields,
            'mapping': self.mapping,
        }
        new_obj = ReadRow(**data)

        if new_obj.errors:
            self.errors.extend(new_obj.errors)
        self.list_objs.append(new_obj)

    def validate_in_file(self):
        # TODO(@slamora) optimize using Counter???
        # https://docs.python.org/3/library/collections.html#collections.Counter
        # this method is for check duplicates unique
        # and unique together fields in the same file
        # before save
        if not hasattr(self.Meta, 'unique_together'):
            return
        l_unique_together = {}
        for i in self.list_objs:
            # unique_together
            t = i.unique_together
            if t in l_unique_together:
                msg = "These fields %s must be unique together values %s"
                msg = msg % (self.Meta.unique_together, t)
                err = {'unique': msg}
                self.add_error(i.line_number, 'unique', err)
            else:
                l_unique_together[t] = None


class ReadRow(object):
    """
    This class build a object from the datas to a row
    """

    def __init__(self, fields=None, mapping=None, meta=None, context=None,
                 line=None, line_number=None):
        self.Meta = meta
        self.fields = fields
        self.mapping = mapping
        self.context = context or {}
        self.line = line
        self.line_number = line_number

        self.data = None
        self.object = None
        self.errors = []

        self.secuence()

    def secuence(self):
        self.get_unique_together()
        try:
            self.build_obj()
            self.create_model()
            self.pre_save()
            self.validate()
        except ValidationError:
            # stop processing the row if there are errors
            # NOTE: errors should be handled inside the functions
            # because there they have more details
            return

        if hasattr(self.Meta, 'save') and self.Meta.save:
            self.save()
            self.post_save()

    def not_create_model(self):
        return hasattr(self.Meta, 'create_model') and \
                not self.Meta.create_model

    def build_obj(self):
        data = {}
        if not self.line: return
        if self.not_create_model(): return

        for csv_fieldname, field in self.fields.items():
            model_fieldname = self.mapping[csv_fieldname]
            try:
                if hasattr(field, 'in_csv') and not field.in_csv:
                    data[model_fieldname] = field.to_python()
                    continue

                if csv_fieldname in self.context:
                    data[model_fieldname] = self.context[csv_fieldname]
                    continue

                cell = self.line[csv_fieldname]
                data[model_fieldname] = field.to_python(cell)
            except ValidationError as error:
                # handle the error here because we know which is the
                # invalid field and we want to provide this info to
                # the user.
                self.add_error(self.line_number, csv_fieldname, str(error))
                raise

        self.data = data

    def create_model(self):
        if not self.data: return
        self.object = self.Meta.dbModel(**self.data)

    def validate(self):
        if not self.object: return
        try:
            self.object.full_clean()
        except ValidationError as e:
            fields = list(e.message_dict.keys())[0]
            self.add_error(self.line_number, fields, e.message_dict)

    def save(self):
        if self.errors: return self.errors
        if not self.object: return
        if hasattr(self.Meta, 'create_model') and not self.Meta.create_model:
            return

        self.object.save()

    def add_error(self, line_number, field, error):
        err_dict = {'line': line_number,
                    'error': {field: error}
                    }
        self.errors.append(err_dict)

    def get_unique_together(self):
        if not self.line: return
        if not hasattr(self.Meta, 'unique_together'):
            return

        t = []
        for u in self.Meta.unique_together:
            t.append(self.line[u])
        self.unique_together = tuple(t)

    def exec_f(self, f):
        try:
            f(self)
        # TODO(@slamora) check which exceptions should be caught
        #   I believe that only none or only ValidationError
        #   handling other execeptions will mask code problems
        #   e.g. missing required context
        except (ValidationError, ValueError, KeyError, ObjectDoesNotExist, DatabaseError) as error:
            file_name = os.path.split(f.__name__)[-1]
            self.add_error(self.line_number, file_name, str(error))

    def pre_save(self):
        if not hasattr(self.Meta, 'pre_save'): return
        for pre in self.Meta.pre_save:
            f = getattr(self.Meta, pre)
            self.exec_f(f)

    def post_save(self):
        if not hasattr(self.Meta, 'post_save'): return
        for post in self.Meta.post_save:
            f = getattr(self.Meta, post)
            self.exec_f(f)
