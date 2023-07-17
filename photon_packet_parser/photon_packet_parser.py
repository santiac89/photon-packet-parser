import io
from photon_packet_parser.message_type import MessageType
from photon_packet_parser.command_type import CommandType
from photon_packet_parser.segmented_package import SegmentedPackage
from photon_packet_parser.protocol16_deserializer import Protocol16Deserializer
from photon_packet_parser.byte_reader import ByteReader
from photon_packet_parser.crc_calculator import CrcCalculator
from photon_packet_parser.number_serializer import NumberSerializer

COMMAND_HEADER_LENGTH = 12
PHOTON_HEADER_LENGTH = 12

class PhotonPacketParser:
    def __init__(self, on_event, on_request, on_response):
        self._pending_segments = {}
        self.on_event = on_event
        self.on_request = on_request
        self.on_response = on_response

    def HandlePayload(self, payload):
        payload = io.BytesIO(payload)

        if (payload.getbuffer().nbytes < PHOTON_HEADER_LENGTH):
            return

        peerId = NumberSerializer.deserialize_short(payload)
        flags = ByteReader.read_byte(payload)[0]
        command_count = ByteReader.read_byte(payload)[0]
        timestamp = NumberSerializer.deserialize_int(payload)
        challenge = NumberSerializer.deserialize_int(payload)
        is_encrypted = flags == 1
        is_crc_enabled = flags == 0xCC

        if (is_encrypted):
            return

        if (is_crc_enabled):
            print("CRC is enabled")
            offset = payload.tell()
            payload.seek(0)
            crc, _ = NumberSerializer.deserialize_int(payload)

            payload.seek(offset)
            payload = NumberSerializer.serialize(0, payload)

            if (crc != CrcCalculator.calculate(payload, payload.getbuffer().nbytes)):
                return

        for _ in range(command_count):
            self.HandleCommand(payload, command_count)

    def HandleCommand(self, source: io.BytesIO, command_count: int):
        command_type = ByteReader.read_byte(source)

        if len(command_type) == 0:
            return

        command_type = command_type[0]
        channel_id = ByteReader.read_byte(source)[0]
        command_flags = ByteReader.read_byte(source)[0]

        source.read(1)

        command_length = NumberSerializer.deserialize_int(source)
        sequence_number = NumberSerializer.deserialize_int(source)

        command_length -= COMMAND_HEADER_LENGTH

        if command_type == CommandType.Disconnect.value:
            return
        elif command_type == CommandType.SendUnreliable.value:
            source.read(4)
            command_length -= 4
            self.HandleSendReliable(source, command_length)
        elif command_type == CommandType.SendReliable.value:
            self.HandleSendReliable(source, command_length)
        elif command_type == CommandType.SendFragment.value:
            self.HandleSendFragment(source, command_length)
        else:
            source.read(command_length)            

    def HandleSendReliable(self,  source: io.BytesIO, command_length: int):
        source.read(1)
        command_length -= 1
        message_type = ByteReader.read_byte(source)[0]
        command_length -= 1
        operation_length = command_length

        payload = io.BytesIO(source.read(operation_length))

        if message_type == MessageType.OperationRequest.value:
            request_data = Protocol16Deserializer.deserialize_operation_request(payload)
            self.on_request(request_data)
        elif message_type == MessageType.OperationResponse.value:
            response_data = Protocol16Deserializer.deserialize_operation_response(payload)
            self.on_request(response_data)
        elif message_type == MessageType.Event.value:
            event_data = Protocol16Deserializer.deserialize_event_data(payload)
            self.on_event(event_data)
        # else:
        #     print("Unknown message type: ", message_type)

    def HandleSendFragment(self, source: io.BytesIO, command_length: int):
        sequence_number = NumberSerializer.deserialize_int(source)
        command_length -= 4
        fragment_count = NumberSerializer.deserialize_int(source)
        command_length -= 4
        fragment_number = NumberSerializer.deserialize_int(source)
        command_length -= 4
        total_length = NumberSerializer.deserialize_int(source)
        command_length -= 4
        fragment_offset = NumberSerializer.deserialize_int(source)
        command_length -= 4

        fragment_length = command_length

        self.HandleSegmentedPayload(sequence_number, total_length, fragment_length, fragment_offset, source)

    def GetSegmentedPackage(self, start_sequence_number, total_length):
        if start_sequence_number in self._pending_segments:
            return self._pending_segments[start_sequence_number]

        segmented_package = SegmentedPackage(total_length=total_length, total_payload=bytearray(total_length))

        self._pending_segments[start_sequence_number] = segmented_package

        return segmented_package
 
    def HandleSegmentedPayload(self, start_sequence_number, total_length, fragment_length, fragment_offset, source):
        segmented_package = self.GetSegmentedPackage(start_sequence_number, total_length)

        for i in range(fragment_length):
            segmented_package.total_payload[fragment_offset + i] = source.read(1)[0]

        segmented_package.bytes_written += fragment_length

        if segmented_package.bytes_written >= segmented_package.total_length:
            self._pending_segments.pop(start_sequence_number)
            self.HandleFinishedSegmentedPackage(segmented_package.total_payload)

    def HandleFinishedSegmentedPackage(self, total_payload: bytearray):
        command_length = len(total_payload)
        self.HandleSendReliable(io.BytesIO(total_payload), command_length)