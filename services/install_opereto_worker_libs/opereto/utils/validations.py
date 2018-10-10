import imghdr
from PIL import Image
import types
import base64
from jsonschema import FormatChecker, validators, Draft4Validator, validate
from jsonschema.exceptions import *

default_variable_pattern = "^[a-z]{1}[a-zA-Z0-9-_]{2,126}$"
default_entity_name_pattern = "^.{0,256}$"

default_variable_name_scheme = {
    "type" : "string",
    "pattern": default_variable_pattern
}

default_entity_name_scheme = {
    "type" : ["string", "null"],
    "pattern": default_entity_name_pattern
}

default_entity_description_scheme = {
    "type" : ["string", "null"],
    "maxLength": 10240
}


services_block_scheme = {
    "type":"object",
    "properties" : {
        "input": {
            "type" : ["object", "null"]
        },
        "service": {
            "type" : "string",
            "pattern": default_variable_pattern
        },
        "title": {
            "type" : ["string","null"],
            "pattern": default_entity_name_pattern
        },
        "agents": {
            "type" : "string",
            "pattern": default_variable_pattern
        }
    },
    "required": ['service'],
    "additionalProperties": True
}

included_services_scheme = {
    'type': ['array', 'null'],
    "items": [
        services_block_scheme
    ]
}

item_properties_scheme = {
    "type":["object", "null"],
    "patternProperties": {
        default_variable_pattern: {
            "type": ["object", "array", "string", "integer", "boolean","null"]
        }
    },
    "additionalProperties": False
}


class JsonSchemeValidator():

    def __init__(self, document, scheme):
        self.document = document
        self.scheme = scheme

        title = scheme.get('title') or 'Scheme'
        self.title = 'Invalid ' + title
        all_validators = dict(Draft4Validator.VALIDATORS)

        MyValidator = validators.create(
            meta_schema=Draft4Validator.META_SCHEMA,
            validators=all_validators
        )
        format_checker = FormatChecker()

        self.validator = MyValidator(
            self.scheme, format_checker=format_checker
        )

    def check_schema(self):
        try:
            self.validator.check_schema(self.scheme)
        except SchemaError,e:
            raise Exception(e)
        except Exception,e:
            raise e

    def validate(self):
        try:
            self.validator.validate(self.document)
        except ValidationError, e:
            if e.schema.get('validationMessage'):
                raise Exception(str(e.schema['validationMessage']))
            if e.path:
                newpath = [str(a) for a in list(e.path)]
                mypath = '->'.join(newpath)
            else:
                raise Exception(e.message)
            raise Exception(e.message)


def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False



def validate_list(list):
    return isinstance(list, types.ListType)

def validate_dict(var):
    return isinstance(var, dict)
       

def validate_string(var):
    return isinstance(var, basestring)


def validate_boolean(var):
    return isinstance(var, bool)

def validate_integer(var):
    if validate_boolean(var):
        return False
    return isinstance(var, (int, long))

def validate_image_file(file):
    if not imghdr.what(file):
        return False
    return True
  
def validate_image_file_size(file, width, height):
    validate_image_file(file)
    im = Image.open(file)
    if im.size[0]!=width or im.size[1]!=height:
        return False
    return True

  
def validate_image_str_size(str, width, height):
    image_str_stripped = base64.b64decode(str)
    try:
        im = Image.fromstring('RGB',(width,height),image_str_stripped)
        return True
    except:
        return False
    

