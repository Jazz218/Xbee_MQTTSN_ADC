from umqttsn import MQTTSN, MQTTSN2
from umqttsn.MQTTSNBase import Packets
import struct

# class Disconnects, class WillTopicUpds, class WillMsgUpds, class WillTopicResps, class WillMsgResps

class Disconnects(Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN2.MessageHeaders(MQTTSN2.DISCONNECT)
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
    assert self.mh.MsgType == MQTTSN2.DISCONNECT
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
    return Packets.__eq__(self, packet) and \
           self.Duration == packet.Duration

class WillTopicUpds(Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN2.MessageHeaders(MQTTSN2.WILLTOPICUPD)
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
    assert self.mh.MsgType == MQTTSN2.WILLTOPICUPD
    pos += self.flags.unpack(buffer[pos:])
    self.WillTopic = buffer[pos:self.mh.Length]

  def __str__(self):
    return str(self.mh)+", Flags "+str(self.flags)+", WillTopic "+str(self.WillTopic)

  def __eq__(self, packet):
    return Packets.__eq__(self, packet) and \
           self.flags == packet.flags and \
           self.WillTopic == packet.WillTopic

class WillMsgUpds(Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN2.MessageHeaders(MQTTSN2.WILLMSGUPD)
    self.WillMsg = ""
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    self.WillMsg = str(self.WillMsg).encode()
    fmt = '>%ds' % len(self.WillMsg)
    return self.mh.pack(len(self.WillMsg)) + struct.pack(fmt, self.WillMsg)

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == MQTTSN2.WILLMSGUPD
    self.WillMsg = buffer[pos:self.mh.Length]

  def __str__(self):
    return str(self.mh)+", WillMsg "+str(self.WillMsg)

  def __eq__(self, packet):
    return Packets.__eq__(self, packet) and \
           self.WillMsg == packet.WillMsg

class WillTopicResps(Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN2.MessageHeaders(MQTTSN2.WILLTOPICRESP)
    self.ReturnCode = 0
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    buffer = MQTTSN.writeInt16(self.ReturnCode)
    return self.mh.pack(len(buffer)) + buffer

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == MQTTSN2.WILLTOPICRESP
    self.ReturnCode = MQTTSN.readInt16(buffer[pos:])

  def __str__(self):
    return str(self.mh)+", ReturnCode "+str(self.ReturnCode)

  def __eq__(self, packet):
    return Packets.__eq__(self, packet) and \
           self.ReturnCode == packet.ReturnCode

class WillMsgResps(Packets):

  def __init__(self, buffer = None):
    self.mh = MQTTSN2.MessageHeaders(MQTTSN2.WILLMSGRESP)
    self.ReturnCode = 0
    if buffer != None:
      self.unpack(buffer)

  def pack(self):
    buffer = MQTTSN.writeInt16(self.ReturnCode)
    return self.mh.pack(len(buffer)) + buffer

  def unpack(self, buffer):
    pos = self.mh.unpack(buffer)
    assert self.mh.MsgType == MQTTSN2.WILLMSGRESP
    self.returnCode = MQTTSN.readInt16(buffer[pos:])

  def __str__(self):
    return str(self.mh)+", ReturnCode "+str(self.ReturnCode)

  def __eq__(self, packet):
    return Packets.__eq__(self, packet) and \
           self.ReturnCode == packet.ReturnCode

objects = [MQTTSN2.Advertises, MQTTSN2.GWInfos, None,
           MQTTSN2.Connects, MQTTSN2.Connacks,
           MQTTSN2.WillTopicReqs, MQTTSN2.WillTopics, MQTTSN2.WillMsgReqs, MQTTSN2.WillMsgs,
           #MQTTSN2.Registers, MQTTSN2.Regacks, MQTTSNclient2.Publishes
           #Subscribes, Subacks, Unsubscribes, Unsubacks,
            Disconnects, None,
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