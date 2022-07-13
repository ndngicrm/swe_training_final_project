from marshmallow import ValidationError


def load_invalid_data_and_assert(schema_class, data):
    try:
        schema_class().load(data)
    except ValidationError:
        assert True
    else:
        assert False
