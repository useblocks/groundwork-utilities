import groundwork
from groundwork_utilities.patterns import GwValidatorsPattern


def test_validator_init():

    class My_Plugin(GwValidatorsPattern):
        def __init__(self, app, **kwargs):
            self.name = "My_Plugin"
            super(My_Plugin, self).__init__(app, **kwargs)

        def activate(self):
            validator = self.validators.register("my_validator", "test validator")

            data = "test this"
            my_hash = validator.hash(data)
            assert validator.validate(data, my_hash) is True
            assert validator.validate("", my_hash) is False

            data = ["test"]
            my_hash = validator.hash(data)
            assert validator.validate(data, my_hash) is True
            assert validator.validate("", my_hash) is False

            data_1 = {"a": ["1", 2, 3], "b": {"ba": "", "bb": None}}
            data_2 = {"a": ["1", 2, 3], "b": {"ba": "1", "bb": None}}
            data_3 = {"a": ["1", 2, 3], "b": {"ba": "", "bb": None}}
            hash_data_1 = validator.hash(data_1)
            assert validator.validate(data_1, hash_data_1) is True
            assert validator.validate(data_2, hash_data_1) is False
            assert validator.validate(data_3, hash_data_1) is True

        def deactivate(self):
            pass

    app = groundwork.App()
    plugin = My_Plugin(app)
    plugin.activate()
