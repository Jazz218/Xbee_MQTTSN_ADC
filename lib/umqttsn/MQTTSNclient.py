from umqttsn import MQTTSN, MQTTSN2, MQTTSN4, MQTTSNinternal, MQTTSNclient2
import xbee


class Callback:

  def __init__(self):
    self.events = []

  def connectionLost(self, cause):
    print("default connectionLost", cause)
    self.events.append("disconnected")

  def messageArrived(self, topicName, payload, qos, retained, msgid):
    print("default publishArrived", topicName, payload, qos, retained, msgid)
    return True

  def deliveryComplete(self, msgid):
    print("default deliveryComplete")
  
  def advertise(self, address, gwid, duration):
    print("advertise", address, gwid, duration)


class TopicMap:

  def __init__(self):
    self.registered = {}

  def register(self, topicId, topicName):
    self.registered[topicId] = topicName

class Client:

  def __init__(self, clientid):
    self.clientid = clientid
    self.msgid = 1
    self.callback = None
    self.__receiver = None
    self.topicmap = TopicMap()
    # self.queue = queue.Queue() # self.Deck = Deck.()

  def start(self):
    self.startReceiver()

  def stop(self):
    MQTTSNclient2.stopReceiver(self)

  def __nextMsgid(self):
    def getWrappedMsgid():
      id = self.msgid + 1
      if id == 65535:
        id = 1
      return id

    if len(self.__receiver.outMsgs) >= 65535:
      raise "No slots left!!"
    else:
      self.msgid = getWrappedMsgid()
      while self.msgid in self.__receiver.outMsgs:
        self.msgid = getWrappedMsgid()
    return self.msgid


  def registerCallback(self, callback):
    self.callback = callback


  def connect(self, cleansession=True):
    connect = MQTTSN2.Connects()
    connect.ClientId = self.clientid
    connect.CleanSession = cleansession
    connect.KeepAliveTimer = 0
    pack = connect.pack()
    print('Pack: {} {}'.format(pack, str(pack)))
    # try:
    #   xbee.transmit(xbee.ADDR_BROADCAST, pack)
    # except Exception as e:
    #   print(e)
    response = MQTTSN4.unpackPacket(MQTTSN.getPacket()) #self.sock
    print('2')
    assert response.mh.MsgType == MQTTSN.CONNACK
    self.startReceiver()


  def startReceiver(self):
    self.__receiver = MQTTSNinternal.Receivers() #self.sock
    if self.callback:
      return
    #id = _thread.start_new_thread(self.__receiver, (self.callback,self.topicmap,self.queue,))


  def waitfor(self, msgType, msgId=None):
    if self.__receiver:
      msg = self.__receiver.waitfor(msgType, msgId)
    else:
      msg = self.__receiver.receive()
      while msg.mh.MsgType != msgType and (msgId == None or msgId == msg.MsgId):
        msg = self.__receiver.receive()
    return msg