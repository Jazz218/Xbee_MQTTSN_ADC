from umqttsn import MQTTSN
from umqttsn.MQTTSNBase import Packets
import struct

# class Packets, class Advertises, class SearchGWs, class GWinfo, class Connects, class Connacks, class WillTopicReqs
# class WillTopics, class WillMsgReqs, class WillMsgs
# Message types

ADVERTISE, SEARCHGW, GWINFO, reserved, \
CONNECT, CONNACK, \
WILLTOPICREQ, WILLTOPIC, WILLMSGREQ, WILLMSG, \
REGISTER, REGACK, \
PUBLISH, PUBACK, PUBCOMP, PUBREC, PUBREL, reserved1, \
SUBSCRIBE, SUBACK, UNSUBSCRIBE, UNSUBACK, \
PINGREQ, PINGRESP, DISCONNECT, reserved2, \
WILLTOPICUPD, WILLTOPICRESP, WILLMSGUPD, WILLMSGRESP = range(30)

packetNames = [ "ADVERTISE", "SEARCHGW", "GWINFO", "reserved",
"CONNECT", "CONNACK",
"WILLTOPICREQ", "WILLTOPIC", "WILLMSGREQ", "WILLMSG",
"REGISTER", "REGACK",
"PUBLISH", "PUBACK", "PUBCOMP", "PUBREC", "PUBREL", "reserved",
"SUBSCRIBE", "SUBACK", "UNSUBSCRIBE", "UNSUBACK",
"PINGREQ", "PINGRESP", "DISCONNECT", "reserved",
"WILLTOPICUPD", "WILLTOPICRESP", "WILLMSGUPD", "WILLMSGRESP"]

class MessageHeaders:

  def __init__(self, aMsgType):
    self.Length = 0
    self.MsgType = aMsgType

  def __eq__(self, mh):
    return self.Length == mh.Length and self.MsgType == mh.MsgType

  def __str__(self):
    "return printable stresentation of our data"
    return "Length " + str(self.Length) + ", " + packetNames[self.MsgType]

  def pack(self, length):
    "pack data into string buffer ready for transmission down socket"
    # length does not yet include the length or msgtype bytes we are going to add
    buffer = self.encode(length) + struct.pack('>B', self.MsgType)
    return buffer

  def encode(self, length):
    self.Length = length + 2
    assert 2 <= self.Length <= 65535
    if self.Length < 256:
      buffer = struct.pack('>B', self.Length)
      # print("length", self.Length)
    else:
      self.Length += 2
      buffer = struct.pack('>B', 1) + MQTTSN.writeInt16(self.Length)
    return buffer

  def unpack(self, buffer):
    "unpack data from string buffer into separate fields"
    (self.Length, bytes) = self.decode(buffer)
    self.MsgType = buffer[bytes]
    return bytes + 1

  def decode(self, buffer):
    value = buffer[0]
    if value > 1:
      bytes = 1
    else:
      value = MQTTSN.readInt16(buffer[1:])
      bytes = 3
    return (value, bytes)

  def writeUTF(aString):
    aString = str(aString).encode()
    fmt = '>%ds' % len(aString)
    return MQTTSN.writeInt16(len(aString)) + struct.pack(fmt, aString)

  def readUTF(buffer):
    length = MQTTSN.readInt16(buffer)
    return buffer[2:2 + length]


class Advertises(Packets):

  def __init__(self, buffer=None):
    self.mh = MessageHeaders(MQTTSN.ADVERTISE)
    self.GwId = 0     # 1 byte
    self.Duration = 0 # 2 bytes
    if buffer:
      self.unpack(buffer)

  def pack(self):
    buffer = struct.pack('>B', self.GwId) + MQTTSN.writeInt16(self.Duration)
    return self.mh.pack(len(buffer)) + buffer

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == MQTTSN.ADVERTISE
    self.GwId = buffer[pos]
    pos += 1
    self.Duration = MQTTSN.readInt16(buffer[pos:])

  def __str__(self):
    return str(self.mh) + " GwId "+str(self.GwId)+" Duration "+str(self.Duration)

  def __eq__(self, packet):
    return Packets.__eq__(self, packet) and \
           self.GwId == packet.GwId and \
           self.Duration == packet.Duration


class GWInfos(Packets):

  def __init__(self, buffer=None):
    self.mh = MessageHeaders(MQTTSN.GWINFO)
    self.GwId = 0  # 1 byte
    self.GwAdd = None # optional
    if buffer:
      self.unpack(buffer)

  def pack(self):
    buffer = struct.pack('>B', self.GwId)
    if self.GwAdd:
      self.GwAdd = str(self.GwAdd).encode()
      fmt = '>%ds' % len(self.GwAdd)
      buffer += struct.pack(fmt, self.GwAdd)
    buffer = self.mh.pack(len(buffer)) + buffer
    return buffer

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == MQTTSN.GWINFO
    self.GwId = buffer[pos]
    pos += 1
    if pos >= self.mh.Length:
      self.GwAdd = None
    else:
      self.GwAdd = buffer[pos:]

  def __str__(self):
    buf = str(self.mh) + " Radius "+str(self.GwId)
    if self.GwAdd:
      buf += " GwAdd "+self.GwAdd
    return buf

class Connects(Packets):

  def __init__(self, buffer=None):
    self.mh = MessageHeaders(MQTTSN.CONNECT)
    self.Flags = MQTTSN.Flags()
    self.ProtocolId = 1
    self.Duration = 30
    self.ClientId = ""
    if buffer!=None:
      self.unpack(buffer)

  def pack(self):
    self.ClientId = str(self.ClientId).encode()
    fmt = '>%ds' % len(self.ClientId)
    header = str(0)
    buffer = self.Flags.pack() + struct.pack('>B', self.ProtocolId) + MQTTSN.writeInt16(self.Duration) + struct.pack(fmt,self.ClientId)
    return self.mh.pack(len(buffer)) + buffer

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == CONNECT
    pos += self.Flags.unpack([buffer[pos]])
    self.ProtocolId = buffer[pos]
    pos += 1
    self.Duration = MQTTSN.readInt16(buffer[pos:])
    pos += 2
    self.ClientId = buffer[pos:]


class Connacks(Packets):

  def __init__(self, buffer = None):
    self.mh = MessageHeaders(CONNACK)
    self.ReturnCode = 0 # 1 byte
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    buffer = struct.pack('>B', self.ReturnCode)
    return self.mh.pack(len(buffer)) + buffer

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == CONNACK
    self.ReturnCode = buffer[pos]

  def __str__(self):
    return str(self.mh)+", ReturnCode "+str(self.ReturnCode)

  def __eq__(self, packet):
    return Packets.__eq__(self, packet) and \
           self.ReturnCode == packet.ReturnCode


class WillTopicReqs(Packets):

  def __init__(self, buffer = None):
    self.mh = MessageHeaders(WILLTOPICREQ)
    if buffer != None:
      self.unpack(buffer)

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == (WILLTOPICREQ)


class WillTopics(Packets):

  def __init__(self, buffer = None):
    self.mh = MessageHeaders(WILLTOPIC)
    self.flags = MQTTSN.Flags()
    self.WillTopic = ""
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    self.WillTopic = str(self.WillTopic).encode()
    fmt = '>%ds' % len(self.WillTopic)
    buffer = self.flags.pack() + struct.pack(fmt, self.WillTopic)
    return self.mh.pack(len(buffer)) + buffer

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == WILLTOPIC
    pos += self.flags.unpack(buffer[pos:])
    self.WillTopic = buffer[pos:self.mh.Length]

  def __str__(self):
    return str(self.mh)+", Flags "+str(self.flags)+", WillTopic "+str(self.WillTopic)

  def __eq__(self, packet):
    return Packets.__eq__(self, packet) and \
           self.flags == packet.flags and \
           self.WillTopic == packet.WillTopic

class WillMsgReqs(Packets):

  def __init__(self, buffer = None):
    self.mh = MessageHeaders(WILLMSGREQ)
    if buffer != None:
      self.unpack(buffer)

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == WILLMSGREQ


class WillMsgs(Packets):

  def __init__(self, buffer = None):
    self.mh = MessageHeaders(WILLMSG)
    self.WillMsg = ""
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    self.WillMsg = str(self.WillMsg).encode()
    fmt = '>%ds' % len(self.WillMsg)
    return self.mh.pack(len(self.WillMsg)) + struct.pack(fmt, self.WillMsg)

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == WILLMSG
    self.WillMsg = buffer[pos:self.mh.Length]

  def __str__(self):
    return str(self.mh)+", WillMsg "+str(self.WillMsg)

  def __eq__(self, packet):
    return Packets.__eq__(self, packet) and \
           self.WillMsg == packet.WillMsg