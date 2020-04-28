import json
from django.core import serializers

def serialize(element):
    return serializers.serialize('json', [element])

def deserialize(element):
    return [x.object for x in serializers.deserialize("json", element)][0]
