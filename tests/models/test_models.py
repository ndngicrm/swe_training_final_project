from main.models.user import UserModel
from tests import data


def test_valid_user():
    invalid_info = [
        # Not in database
        ("dsakbdaks@dsjs.com", "sdajhaksh"),
        ("haibabon@yahoo.com", "sdasa"),
        # Wrong password
        ("nghia1@gmail.com", "Aa123456aaaa"),
        ("nghia2@yahoo.com", "AAAaaa111aaaa"),
        ("nghia3@postman.com", "AA@aa111!aa"),
        ("nghia4.nd@aaaa.com", "AAA!!!a111!aa"),
    ]

    for info in invalid_info:
        assert not UserModel.get_user_id(*info)

    for info in data.users_info:
        assert UserModel.get_user_id(*info)
