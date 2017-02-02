import pytest
from sqlalchemy import  Column, String, Integer

import groundwork
from groundwork_utilities.patterns import GwDbValidatorsPattern
from groundwork_utilities.patterns.gw_db_validators_pattern.gw_db_validators import ValidationError


def test_db_validator_init():

    class My_Plugin(GwDbValidatorsPattern):
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

            self.validators.db.register("db_test_validator", "my db test validator", self.Test)

            my_test = self.Test(name="blub")
            self.db.add(my_test)
            self.db.commit()
            self.db.query(self.Test).all()

            my_test.name = "Boohaaaa"
            self.db.add(my_test)
            self.db.commit()
            self.db.query(self.Test).all()

            # Execute sql-statement, which does not trigger the sqlalchemy events. So no hash gets updated.
            self.db.engine.execute("UPDATE test SET name='not_working' WHERE id=1")

            # Add another entry, so the query are executed on database and not on session
            # ( self.db.session.remove() does not do the trick, y?? )
            my_test_2 = self.Test(name="blub")
            self.db.add(my_test_2)
            self.db.commit()

            with pytest.raises(ValidationError):
                self.db.query(self.Test).filter_by(id=1).first()

        def deactivate(self):
            pass

    app = groundwork.App()
    plugin = My_Plugin(app)
    plugin.activate()
