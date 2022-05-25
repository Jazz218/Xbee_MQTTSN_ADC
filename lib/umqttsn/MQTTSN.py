
import struct
import xbee

# class Flags (__init__, __eq__, __ne__, __str__)
# def writeInt16, readInt16, getPacket, MessageType, pack, unpack

# Low-level protocol interface for MQTTs

# Message types
ADVERTISE, SEARCHGW, GWINFO, reserved, \
CONNECT, CONNACK, \
WILLTOPICREQ, WILLTOPIC, WILLMSGREQ, WILLMSG, \
REGISTER, REGACK, \
PUBLISH, PUBACK, PUBCOMP, PUBREC, PUBREL, reserved1, \
SUBSCRIBE, SUBACK, UNSUBSCRIBE, UNSUBACK, \
PINGREQ, PINGRESP, DISCONNECT, reserved2, \
WILLTOPICUPD, WILLTOPICRESP, WILLMSGUPD, WILLMSGRESP = range(30)

packetNames = ["ADVERTISE", "SEARCHGW", "GWINFO", "reserved",
               "CONNECT", "CONNACK",
               "WILLTOPICREQ", "WILLTOPIC", "WILLMSGREQ", "WILLMSG",
               "REGISTER", "REGACK",
               "PUBLISH", "PUBACK", "PUBCOMP", "PUBREC", "PUBREL", "reserved",
               "SUBSCRIBE", "SUBACK", "UNSUBSCRIBE", "UNSUBACK",
               "PINGREQ", "PINGRESP", "DISCONNECT", "reserved",
               "WILLTOPICUPD", "WILLTOPICRESP", "WILLMSGUPD", "WILLMSGRESP"]

TopicIdType_Names = ["NORMAL", "PREDEFINED", "SHORT_NAME"]
TOPIC_NORMAL, TOPIC_PREDEFINED, TOPIC_SHORTNAME = range(3)


def writeInt16(length):
    return struct.pack('>H', length)

def readInt16(buf):
    return buf[0] * 256 + buf[1]

def getPacket(aSocket=False):
    "receive the next packet"
    #buf, address = aSocket.recvfrom(1000)  # get the first byte fixed header
    buf = xbee.receive()
    print("RECEIVE BUF: {}".format(buf))
    address="0.0.0.0"
    if buf == "":
        return None
    length = buf[0]
    if length == 1:
        if buf == "":
            return None
        length = readInt16(buf[1:])
    return buf, address


def MessageType(buf):
    if buf[0] == 1:
        msgtype = buf[3]
    else:
        msgtype = buf[1]
    return msgtype


class Flags:
    def __init__(self):
        self.DUP = False  # 1 bit
        self.QoS = 0  # 2 bits
        self.Retain = False  # 1 bit
        self.Will = False  # 1 bit
        self.CleanSession = True  # 1 bit
        self.TopicIdType = 0  # 2 bits

    def __eq__(self, flags):
        return self.DUP == flags.DUP and \
               self.QoS == flags.QoS and \
               self.Retain == flags.Retain and \
               self.Will == flags.Will and \
               self.CleanSession == flags.CleanSession and \
               self.TopicIdType == flags.TopicIdType

    def __ne__(self, flags):
        return not self.__eq__(flags)

    def __str__(self):
        "return printable representation of our data"
        return '{DUP ' + str(self.DUP) + \
               ", QoS " + str(self.QoS) + ", Retain " + str(self.Retain) + \
               ", Will " + str(self.Will) + ", CleanSession " + str(self.CleanSession) + \
               ", TopicIdType " + str(self.TopicIdType) + "}"

    def pack(self):
        "pack data into string buffer ready for transmission down socket"
        buffer = (self.DUP << 7) | (self.QoS << 5) | (self.Retain << 4) | \
                 (self.Will << 3) | (self.CleanSession << 2) | self.TopicIdType
        buffer = struct.pack('>B', buffer)
        # print("Flags - pack", str(bin(ord(buffer))), len(buffer))
        return buffer

    def unpack(self, buffer):
        "unpack data from string buffer into separate fields"
        b0 = buffer[0]
        # print("Flags - unpack", str(bin(b0)), len(buffer), buffer)
        self.DUP = ((b0 >> 7) & 0x01) == 1
        self.QoS = (b0 >> 5) & 0x03
        self.Retain = ((b0 >> 4) & 0x01) == 1
        self.Will = ((b0 >> 3) & 0x01) == 1
        self.CleanSession = ((b0 >> 2) & 0x01) == 1
        self.TopicIdType = (b0 & 0x03)
        return 1