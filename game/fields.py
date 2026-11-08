from decimal import Decimal
from django.db import models


class MoneyField(models.DecimalField):


    def get_internal_type(self):

        return 'TextField'

    def db_type(self, connection):
        if connection.vendor == 'sqlite':
            return 'text'
        return connection.data_types['DecimalField'] % self.db_type_parameters(connection)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return Decimal(str(value)).quantize(Decimal('0.01'))
