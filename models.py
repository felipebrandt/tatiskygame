from datetime import datetime, timedelta
from peewee import *
from db_connection import db, OPTIONS


class BaseModel(Model):
    created_at = DateTimeField()
    updated_at = DateTimeField(null=True)

    class Meta:
        database = db

    def save_model(self, data_model):
        self.save()


class SpinDay(BaseModel):
    spin_day_id = AutoField(primary_key=True)
    round_amount = IntegerField()
    is_valid = BooleanField()


class Round(BaseModel):
    round_id = AutoField(primary_key=True)
    spin_day = ForeignKeyField(SpinDay, to_field='spin_day_id')
    result = CharField(max_length=255)


class Webhook(BaseModel):
    webhook_id = AutoField(primary_key=True, help_text='Id do webhook')
    raw_data = TextField()


if __name__ == '__main__':
    db.create_tables([SpinDay, Round])