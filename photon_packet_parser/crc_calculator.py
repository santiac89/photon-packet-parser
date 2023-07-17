class CrcCalculator:
    @staticmethod
    def calculate(_bytes, length):
        result = 4294967295
        key = 3988292384

        i = 0
        while i < length:
            result ^= _bytes[i]

            j = 0
            while j < 8:
                if ((result & 1) > 0):
                    result = result >> 1 ^ key
                else:
                    result >>= 1

                j += 1

            i += 1

        return result