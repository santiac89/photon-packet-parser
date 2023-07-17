import io

class NumberSerializer:
    @staticmethod
    def deserialize_int(source: io.BytesIO):
        value1 = source.read(1)[0] << 24
        value2 = value1 | (source.read(1)[0] << 16)
        value3 = value2 | (source.read(1)[0] << 8)
        value = (value3 | source.read(1)[0])
        return value

    @staticmethod
    def deserialize_short(source: io.BytesIO):
        value1 = (source.read(1)[0] << 8)
        value = (value1 | source.read(1)[0])
        return value

    @staticmethod
    def serialize(value, target: io.BytesIO):
        target.write(value >> 24)
        target.write(value >> 16)
        target.write(value >> 8)
