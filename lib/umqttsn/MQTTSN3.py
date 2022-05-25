import struct
from umqttsn import MQTTSN, MQTTSN2 #, MQTTSNclient2
from umqttsn import MQTTSNBase
from umqttsn.MQTTSNBase import Packets

# class Pubacks, class Pubrecs, class Pubrels, class Pubcomps
# class Pingreqs, class Pingresps

#deleted Subscribes, Subacks, Unsubscribes, Unsubacks

# Message types


TopicIdType_Names = ["NORMAL", "PREDEFINED", "SHORT_NAME"]
TOPIC_NORMAL, TOPIC_PREDEFINED, TOPIC_SHORTNAME = range(3)


class Pubacks(Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN2.MessageHeaders(MQTTSNBase.PUBACK)
    self.TopicId = 0
    self.MsgId = 0
    self.ReturnCode = 0 # 1 byte
    if buffer != None:
      self.mh.unpack(buffer)

  def pack(self):
    buffer = MQTTSN.writeInt16(self.TopicId) + MQTTSN.writeInt16(self.MsgId) + struct.pack('>B', self.ReturnCode)
    return self.mh.pack(len(buffer)) + buffer

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == MQTTSNBase.PUBACK
    self.TopicId = MQTTSN.readInt16(buffer[pos:])
    pos += 2
    self.MsgId = MQTTSN.readInt16(buffer[pos:])
    pos += 2
    self.ReturnCode = buffer[pos]

  def __str__(self):
    return str(self.mh)+", TopicId "+str(self.TopicId)+" , MsgId "+str(self.MsgId)+", ReturnCode "+str(self.ReturnCode)

  def __eq__(self, packet):
    return Packets.__eq__(self, packet) and \
           self.TopicId == packet.TopicId and \
           self.MsgId == packet.MsgId and \
           self.ReturnCode == packet.ReturnCode


class Pubrecs(Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN2.MessageHeaders(MQTTSNBase.PUBREC)
    self.MsgId = 0
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    return self.mh.pack(2) + MQTTSN.writeInt16(self.MsgId)

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == MQTTSNBase.PUBREC
    self.MsgId = MQTTSN.readInt16(buffer[pos:])

  def __str__(self):
    return str(self.mh)+" , MsgId "+str(self.MsgId)

  def __eq__(self, packet):
    return Packets.__eq__(self, packet) and self.MsgId == packet.MsgId

class Pubrels(Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN2.MessageHeaders(MQTTSNBase.PUBREL)
    self.MsgId = 0
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    return self.mh.pack(2) + MQTTSN.writeInt16(self.MsgId)

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == MQTTSNBase.PUBREL
    self.MsgId = MQTTSN.readInt16(buffer[pos:])

  def __str__(self):
    return str(self.mh)+" , MsgId "+str(self.MsgId)

  def __eq__(self, packet):
    return Packets.__eq__(self, packet) and self.MsgId == packet.MsgId


class Pubcomps(Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN2.MessageHeaders(MQTTSNBase.PUBCOMP)
    self.MsgId = 0
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    return self.mh.pack(2) + MQTTSN.writeInt16(self.MsgId)

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == MQTTSNBase.PUBCOMP
    self.MsgId = (buffer[pos:])

  def __str__(self):
    return str(self.mh)+" , MsgId "+str(self.MsgId)

  def __eq__(self, packet):
    return Packets.__eq__(self, packet) and self.MsgId == packet.MsgId