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

class Packets():

  def pack(self):
    print("Packets pack")
    return self.mh.pack(0)

  def __str__(self):
    return str(self.mh)

  def __eq__(self, packet):
    return False if packet == None else self.mh == packet.mh

  def __ne__(self, packet):
    return not self.__eq__(packet)