import pytest
from sqlalchemy import Column, String, Integer

import groundwork
from groundwork_utilities.plugins import GwDbValidator
from groundwork_database.patterns import GwSqlPattern
from groundwork_utilities.patterns.gw_db_validators_pattern.gw_db_validators import ValidationError


def test_plugin_init():

    app = groundwork.App()
    validator_plugin = GwDbValidator(app)
    validator_plugin.activate()


def test_validation():

    app = groundwork.App()
    validator_plugin = GwDbValidator(app)
    validator_plugin.activate()

    class My_Plugin(GwSqlPattern):
        def __init__(self, app, **kwargs):
            self.name = "My_Plugin"
            super(My_Plugin, self).__init__(app, **kwargs)
            self.db = None
            self.Test = None

        def activate(self):
            self.db = self.app.databases.register("test_db",
                                                  "sqlite://",
                                                  "database for test values")

            class Test(self.db.Base):
                __tablename__ = "test"
                id = Column(Integer, primary_key=True)
                name = Column(String(512), nullable=False, unique=True)

            self.Test = self.db.classes.register(Test)
            self.db.create_all()

    test_plugin = My_Plugin(app)
    test_plugin.activate()

    test_entry_1 = test_plugin.Test(name="blub")
    test_plugin.db.add(test_entry_1)
    test_plugin.db.commit()

    assert test_plugin.Test.query.count() == 1

    hash_db = app.databases.get("hash_db")
    hash_db_model = hash_db.classes.get("Hashes")
    assert hash_db is not None
    assert hash_db_model is not None
    assert hash_db_model.query.count() == 1
    test_plugin.Test.query.all()

    test_entry_2 = test_plugin.Test(name="Yehaa")
    test_plugin.db.add(test_entry_2)
    test_plugin.db.commit()
    assert hash_db_model.query.count() == 2

    # Let's change data without triggering the sqlalchemy events, so that the hash gets not updated.
    test_plugin.db.engine.execute("UPDATE test SET name='not_working' WHERE id=1")

    # Now tell sqlalchemy to refresh/reload the object
    with pytest.raises(ValidationError):
        test_plugin.db.session.refresh(test_entry_1)

    # Let's change our object the normal way and add the changes to the db.
    test_entry_1.name = "Boohaaa"
    test_plugin.db.add(test_entry_1)
    test_plugin.db.commit()
    test_plugin.db.session.refresh(test_entry_1)
