import io

class ByteReader:
    @staticmethod
    def read_byte(payload: io.BytesIO):
        return payload.read(1)