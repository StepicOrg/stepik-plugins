import datetime
import json

from decimal import Decimal

from stepic_plugins.schema import RPCSerializer


class TestRPCSerializer(object):
    def transfer_data(self, data):
        serializer = RPCSerializer()
        serialized_data = json.dumps(serializer.serialize_entity(None, data))
        return serializer.deserialize_entity(None, json.loads(serialized_data))

    def test_serialize_decimal(self):
        number = Decimal('10.12345678901234567890')

        transferred_number = self.transfer_data(number)

        assert transferred_number == number

    def test_serialize_datetime(self):
        dt = datetime.datetime(2016, 5, 3, 14, 20, 49, 123456)

        transferred_dt = self.transfer_data(dt)

        assert transferred_dt == dt

    def test_serialize_date(self):
        date = datetime.date(2016, 5, 31)

        transferred_date = self.transfer_data(date)

        assert transferred_date == date

    def test_serialize_timedelta(self):
        td = datetime.timedelta(seconds=43463, microseconds=1234)

        transferred_td = self.transfer_data(td)

        assert transferred_td == td
