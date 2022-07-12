from marshmallow import ValidationError


def load_invalid_data_and_assert(Schema, data):
    try:
        Schema().load(data)
    except ValidationError:
        assert True
    else:
        assert False
