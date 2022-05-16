import struct
import MQTTSN
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

packetNames = [ "ADVERTISE", "SEARCHGW", "GWINFO", "reserved",
"CONNECT", "CONNACK",
"WILLTOPICREQ", "WILLTOPIC", "WILLMSGREQ", "WILLMSG",
"REGISTER", "REGACK",
"PUBLISH", "PUBACK", "PUBCOMP", "PUBREC", "PUBREL", "reserved",
"SUBSCRIBE", "SUBACK", "UNSUBSCRIBE", "UNSUBACK",
"PINGREQ", "PINGRESP", "DISCONNECT", "reserved",
"WILLTOPICUPD", "WILLTOPICRESP", "WILLMSGUPD", "WILLMSGRESP"]

TopicIdType_Names = ["NORMAL", "PREDEFINED", "SHORT_NAME"]
TOPIC_NORMAL, TOPIC_PREDEFINED, TOPIC_SHORTNAME = range(3)


class Pubacks(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(PUBACK)
    self.TopicId = 0
    self.MsgId = 0
    self.ReturnCode = 0 # 1 byte
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    buffer = MQTTSN.writeInt16(self.TopicId) + MQTTSN.writeInt16(self.MsgId) + struct.pack('>B', self.ReturnCode)
    return self.mh.pack(len(buffer)) + buffer

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == PUBACK
    self.TopicId = MQTTSN.readInt16(buffer[pos:])
    pos += 2
    self.MsgId = MQTTSN.readInt16(buffer[pos:])
    pos += 2
    self.ReturnCode = buffer[pos]

  def __str__(self):
    return str(self.mh)+", TopicId "+str(self.TopicId)+" , MsgId "+str(self.MsgId)+", ReturnCode "+str(self.ReturnCode)

  def __eq__(self, packet):
    return MQTTSN.Packets.__eq__(self, packet) and \
           self.TopicId == packet.TopicId and \
           self.MsgId == packet.MsgId and \
           self.ReturnCode == packet.ReturnCode


class Pubrecs(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(PUBREC)
    self.MsgId = 0
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    return self.mh.pack(2) + MQTTSN.writeInt16(self.MsgId)

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == PUBREC
    self.MsgId = MQTTSN.readInt16(buffer[pos:])

  def __str__(self):
    return str(self.mh)+" , MsgId "+str(self.MsgId)

  def __eq__(self, packet):
    return MQTTSN.Packets.__eq__(self, packet) and self.MsgId == packet.MsgId

class Pubrels(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(PUBREL)
    self.MsgId = 0
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    return self.mh.pack(2) + MQTTSN.writeInt16(self.MsgId)

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == PUBREL
    self.MsgId = MQTTSN.readInt16(buffer[pos:])

  def __str__(self):
    return str(self.mh)+" , MsgId "+str(self.MsgId)

  def __eq__(self, packet):
    return MQTTSN.Packets.__eq__(self, packet) and self.MsgId == packet.MsgId


class Pubcomps(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(PUBCOMP)
    self.MsgId = 0
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    return self.mh.pack(2) + MQTTSN.writeInt16(self.MsgId)

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == PUBCOMP
    self.MsgId = (buffer[pos:])

  def __str__(self):
    return str(self.mh)+" , MsgId "+str(self.MsgId)

  def __eq__(self, packet):
    return MQTTSN.Packets.__eq__(self, packet) and self.MsgId == packet.MsgId


class Subscribes(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(SUBSCRIBE)
    self.Flags = MQTTSN.Flags()
    self.MsgId = 0 # 2 bytes
    self.TopicId = 0 # 2 bytes
    self.TopicName = ""
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    buffer = self.Flags.pack() + MQTTSN.writeInt16(self.MsgId)
    if self.Flags.TopicIdType == TOPIC_PREDEFINED:
      buffer += MQTTSN.writeInt16(self.TopicId)
    elif self.Flags.TopicIdType in [TOPIC_NORMAL, TOPIC_SHORTNAME]:
      self.TopicName = str(self.TopicName).encode()
      fmt = '>%ds' % len(self.TopicName)
      buffer += struct.pack(fmt, self.TopicName)
    return self.mh.pack(len(buffer)) + buffer


  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == SUBSCRIBE
    pos += self.Flags.unpack(buffer[pos:])
    self.MsgId = MQTTSN.readInt16(buffer[pos:])
    pos += 2
    self.TopicId = 0
    self.TopicName = ""
    if self.Flags.TopicIdType == TOPIC_PREDEFINED:
      self.TopicId = MQTTSN.readInt16(buffer[pos:])
    elif self.Flags.TopicIdType in [TOPIC_NORMAL, TOPIC_SHORTNAME]:
      self.TopicName = buffer[pos:pos+2]

  def __str__(self):
    buffer = str(self.mh)+", Flags "+str(self.Flags)+", MsgId "+str(self.MsgId)
    if self.Flags.TopicIdType == 0:
      buffer += ", TopicName "+str(self.TopicName)
    elif self.Flags.TopicIdType == 1:
      buffer += ", TopicId "+str(self.TopicId)
    elif self.Flags.TopicIdType == 2:
      buffer += ", TopicId "+str(self.TopicId)
    return buffer

  def __eq__(self, packet):
    if self.Flags.TopicIdType == 0:
      if packet == None:
        rc = False
      else:
        rc = self.TopicName == packet.TopicName
    else:
      if packet == None:
        rc = False
      else:
        rc = self.TopicId == packet.TopicId
    return MQTTSN.Packets.__eq__(self, packet) and \
         self.Flags == packet.Flags and \
         self.MsgId == packet.MsgId and rc


class Subacks(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(SUBACK)
    self.Flags = MQTTSN.Flags() # 1 byte
    self.TopicId = 0 # 2 bytes
    self.MsgId = 0 # 2 bytes
    self.ReturnCode = 0 # 1 byte
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    buffer = self.Flags.pack() + MQTTSN.writeInt16(self.TopicId) + MQTTSN.writeInt16(self.MsgId) + struct.pack('>B', self.ReturnCode)
    return self.mh.pack(len(buffer)) + buffer

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == SUBACK
    pos += self.Flags.unpack(buffer[pos:])
    self.TopicId = MQTTSN.readInt16(buffer[pos:])
    pos += 2
    self.MsgId = MQTTSN.readInt16(buffer[pos:])
    pos += 2
    self.ReturnCode = buffer[pos]

  def __str__(self):
    return str(self.mh)+", Flags "+str(self.Flags)+", TopicId "+str(self.TopicId)+" , MsgId "+str(self.MsgId)+", ReturnCode "+str(self.ReturnCode)

  def __eq__(self, packet):
    return MQTTSN.Packets.__eq__(self, packet) and \
           self.Flags == packet.Flags and \
           self.TopicId == packet.TopicId and \
           self.MsgId == packet.MsgId and \
           self.ReturnCode == packet.ReturnCode


class Unsubscribes(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(UNSUBSCRIBE)
    self.Flags = MQTTSN.Flags()
    self.MsgId = 0 # 2 bytes
    self.TopicId = 0 # 2 bytes
    self.TopicName = ""
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    buffer = self.Flags.pack() + MQTTSN.writeInt16(self.MsgId)
    if self.Flags.TopicIdType == 0:
      self.TopicName = str(self.TopicName).encode()
      fmt = '>%ds' % len(self.TopicName)
      buffer += struct.pack(fmt, self.TopicName)
    elif self.Flags.TopicIdType == 1:
      buffer += MQTTSN.writeInt16(self.TopicId)
    elif self.Flags.TopicIdType == 2:
      self.TopicId = str(self.TopicId).encode()
      fmt = '>%ds' % len(self.TopicId)
      buffer += struct.pack(fmt, self.TopicId)
    return self.mh.pack(len(buffer)) + buffer

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == UNSUBSCRIBE
    pos += self.Flags.unpack(buffer[pos:])
    self.MsgId = MQTTSN.readInt16(buffer[pos:])
    pos += 2
    self.TopicId = 0
    self.TopicName = ""
    if self.Flags.TopicIdType == 0:
      self.TopicName = buffer[pos:self.mh.Length]
    elif self.Flags.TopicIdType == 1:
      self.TopicId = MQTTSN.readInt16(buffer[pos:])
    elif self.Flags.TopicIdType == 3:
      self.TopicId = buffer[pos:pos+2]

  def __str__(self):
    buffer = str(self.mh)+", Flags "+str(self.Flags)+", MsgId "+str(self.MsgId)
    if self.Flags.TopicIdType == 0:
      buffer += ", TopicName "+str(self.TopicName)
    elif self.Flags.TopicIdType == 1:
      buffer += ", TopicId "+str(self.TopicId)
    elif self.Flags.TopicIdType == 2:
      buffer += ", TopicId "+str(self.TopicId)
    return buffer

  def __eq__(self, packet):
    return MQTTSN.Packets.__eq__(self, packet) and \
         self.Flags == packet.Flags and \
         self.MsgId == packet.MsgId and \
         self.TopicId == packet.TopicId and \
         self.TopicName == packet.TopicName

class Unsubacks(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(UNSUBACK)
    self.MsgId = 0
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    return self.mh.pack(2) + MQTTSN.writeInt16(self.MsgId)

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == UNSUBACK
    self.MsgId = MQTTSN.readInt16(buffer[pos:])

  def __str__(self):
    return str(self.mh)+" , MsgId "+str(self.MsgId)

  def __eq__(self, packet):
    return MQTTSN.Packets.__eq__(self, packet) and self.MsgId == packet.MsgId


class Pingreqs(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(PINGREQ)
    self.ClientId = None
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    if self.ClientId:
      self.ClientId = str(self.ClientId).encode()
      fmt = '>%ds' % len(self.ClientId)
      buf = self.mh.pack(len(self.ClientId)) + struct.pack(fmt, self.ClientId)
    else:
      buf = self.mh.pack(0)
    return buf

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == PINGREQ
    self.ClientId = buffer[pos:self.mh.Length]
    if self.ClientId == b'':
      self.ClientId = None

  def __str__(self):
    buf = str(self.mh)
    if self.ClientId:
      buf += ", ClientId "+str(self.ClientId)
    return buf

  def __eq__(self, packet):
    return MQTTSN.Packets.__eq__(self, packet) and \
           self.ClientId == packet.ClientId


class Pingresps(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(PINGRESP)
    if buffer != None:
      self.unpack(buffer)

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == PINGRESP

class Disconnects(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(DISCONNECT)
    self.Duration = None
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    if self.Duration:
      buf = self.mh.pack(2) + MQTTSN.writeInt16(self.Duration)
    else:
      buf = self.mh.pack(0)
    return buf

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == DISCONNECT
    buf = buffer[pos:self.mh.Length]
    if buf == b'':
      self.Duration = None
    else:
      self.Duration = MQTTSN.readInt16(buffer[pos:])

  def __str__(self):
    buf = str(self.mh)
    if self.Duration:
      buf += ", Duration "+str(self.Duration)
    return buf

  def __eq__(self, packet):
    return MQTTSN.Packets.__eq__(self, packet) and \
           self.Duration == packet.Duration

class WillTopicUpds(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(WILLTOPICUPD)
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
    assert self.mh.MsgType == WILLTOPICUPD
    pos += self.flags.unpack(buffer[pos:])
    self.WillTopic = buffer[pos:self.mh.Length]

  def __str__(self):
    return str(self.mh)+", Flags "+str(self.flags)+", WillTopic "+str(self.WillTopic)

  def __eq__(self, packet):
    return MQTTSN.Packets.__eq__(self, packet) and \
           self.flags == packet.flags and \
           self.WillTopic == packet.WillTopic

class WillMsgUpds(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(WILLMSGUPD)
    self.WillMsg = ""
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    self.WillMsg = str(self.WillMsg).encode()
    fmt = '>%ds' % len(self.WillMsg)
    return self.mh.pack(len(self.WillMsg)) + struct.pack(fmt, self.WillMsg)

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == WILLMSGUPD
    self.WillMsg = buffer[pos:self.mh.Length]

  def __str__(self):
    return str(self.mh)+", WillMsg "+str(self.WillMsg)

  def __eq__(self, packet):
    return MQTTSN.Packets.__eq__(self, packet) and \
           self.WillMsg == packet.WillMsg

class WillTopicResps(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(WILLTOPICRESP)
    self.ReturnCode = 0
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    buffer = MQTTSN.writeInt16(self.ReturnCode)
    return self.mh.pack(len(buffer)) + buffer

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == WILLTOPICRESP
    self.ReturnCode = MQTTSN.readInt16(buffer[pos:])

  def __str__(self):
    return str(self.mh)+", ReturnCode "+str(self.ReturnCode)

  def __eq__(self, packet):
    return MQTTSN.Packets.__eq__(self, packet) and \
           self.ReturnCode == packet.ReturnCode

class WillMsgResps(MQTTSN.Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN.MessageHeaders(WILLMSGRESP)
    self.ReturnCode = 0
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    buffer = MQTTSN.writeInt16(self.ReturnCode)
    return self.mh.pack(len(buffer)) + buffer

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == WILLMSGRESP
    self.returnCode = MQTTSN.readInt16(buffer[pos:])

  def __str__(self):
    return str(self.mh)+", ReturnCode "+str(self.ReturnCode)

  def __eq__(self, packet):
    return MQTTSN.Packets.__eq__(self, packet) and \
           self.ReturnCode == packet.ReturnCode

objects = [MQTTSN.Advertises, MQTTSN.SearchGWs, MQTTSN.GWInfos, None,
           MQTTSN.Connects, MQTTSN.Connacks,
           MQTTSN.WillTopicReqs, MQTTSN.WillTopics, MQTTSN.WillMsgReqs, MQTTSN.WillMsgs,
           MQTTSN.Registers, MQTTSN.Regacks,
           MQTTSN.Publishes, Pubacks, Pubcomps, Pubrecs, Pubrels, None,
           Subscribes, Subacks, Unsubscribes, Unsubacks,
           Pingreqs, Pingresps, Disconnects, None,
           WillTopicUpds, WillTopicResps, WillMsgUpds, WillMsgResps]

def unpackPacket(msg):
  (buffer, address) = msg
  if MQTTSN.MessageType(buffer) != None:
    packet = objects[MQTTSN.MessageType(buffer)]()
    packet.unpack(buffer)
  else:
    packet = None
  return packet, address

if __name__ == "__main__":
  print("Object string representations")
  for o in objects:
    if o:
      print(o())

  print("\nComparisons")
  for o in [MQTTSN.Flags] + objects:
    if o:
      o1 = o()
      o2 = o()
      o2.unpack(o1.pack())
      if o1 != o2:
        print("error! ", str(o1.mh) if hasattr(o1, "mh") else o1.__class__.__name__)
        print(str(o1))
        print(str(o2))
      else:
        print("ok ", str(o1.mh) if hasattr(o1, "mh") else o1.__class__.__name__)
