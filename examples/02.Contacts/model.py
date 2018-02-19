from peewee import *

db = SqliteDatabase('./examples/02.Contacts/people.db')

class Person(Model):
    name = CharField()
    birthday = DateField()
    is_relative = BooleanField()

    class Meta:
        database = db # This model uses the "people.db" database.

if __name__ == "__main__":
    db.connect()
    db.create_tables([Person])
