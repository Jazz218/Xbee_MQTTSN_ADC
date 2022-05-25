# import xbee, MQTTSNclient

from umqttsn import MQTTSN, MQTTSN2, MQTTSN3

def register(self, topicName):
    register = MQTTSN3.Registers()
    register.TopicName = topicName
    if self.__receiver:
        self.__receiver.lookfor(MQTTSN.REGACK)
        self.xbee.transmit(register.pack())
    msg = self.waitfor(MQTTSN.REGACK, register.MsgId)
    self.topicmap.register(msg.TopicId, topicName)
    return msg.TopicId


def publish(self, topic, payload, qos=0, retained=False):
    if isinstance(payload, str) or isinstance(payload, bytes):
        pass
    else:
        raise TypeError('Payload must be str or bytes.')
    publish = MQTTSN.Publishes()
    publish.Flags.QoS = qos
    publish.Flags.Retain = retained
    if isinstance(topic, str):
        publish.Flags.TopicIdType = MQTTSN.TOPIC_SHORTNAME
        publish.TopicName = topic
    else:
        publish.Flags.TopicIdType = MQTTSN.TOPIC_NORMAL
        publish.TopicId = topic
    if qos in [-1, 0]:
        publish.MsgId = 0
    else:
        publish.MsgId = self.__nextMsgid()
        # print("MsgId", publish.MsgId)
        self.__receiver.outMsgs[publish.MsgId] = publish
    publish.Data = payload
    self.xbee.transmit(publish.pack())
    return publish.MsgId


def disconnect(self):
    disconnect = MQTTSN2.Disconnects()
    if self.__receiver:
        self.__receiver.lookfor(MQTTSN.DISCONNECT)
    msg = self.waitfor(MQTTSN.DISCONNECT)
    self.stopReceiver()


def stopReceiver(self):
    assert self.__receiver.inMsgs == {}
    assert self.__receiver.outMsgs == {}
    self.__receiver = None


def receive(self):
    return self.__receiver.receive()


# def publish(topic, payload, retained=False, port=1883, host="localhost"):
#     publish = MQTTSN.Publishes()
#     publish.Flags.QoS = 3
#     publish.Flags.Retain = retained
#     if isinstance(payload, str):
#         pass
#     elif isinstance(payload, bytes):
#         payload = payload.decode()
#     if isinstance(topic, str):
#         if len(topic) > 2:
#             publish.Flags.TopicIdType = MQTTSN.TOPIC_NORMAL
#             publish.TopicId = len(topic)
#             payload = topic + payload
#         else:
#             publish.Flags.TopicIdType = MQTTSN.TOPIC_SHORTNAME
#             publish.TopicName = topic
#     else:
#         publish.Flags.TopicIdType = MQTTSN.TOPIC_NORMAL
#         publish.TopicId = topic
#     publish.MsgId = 0
#     # print("payload", payload)
#     publish.Data = payload
#     xbee.transmit(publish.pack(), (host, port))
#     return


if __name__ == "__main__":
    """
  mclient = Client("myclientid", host="225.0.18.83", port=1883)
  mclient.registerCallback(Callback())
  mclient.start()

  publish("long topic name", "qos -1 start", port=1884)

  callback = Callback()

  aclient = Client("myclientid", port=1884)
  aclient.registerCallback(callback)

  aclient.connect()
  aclient.disconnect()

  aclient.connect()
  aclient.subscribe("k ", 2)
  aclient.subscribe("jkjkjkjkj", 2)
  aclient.publish("k ", "qos 0")
  aclient.publish("k ", "qos 1", 1)
  aclient.publish("jkjkjkjkj", "qos 2", 2)
  topicid = aclient.register("jkjkjkjkj")
  #time.sleep(1.0)
  aclient.publish(topicid, "qos 2 - registered topic id", 2)
  #time.sleep(1.0)
  aclient.disconnect()
  publish("long topic name", "qos -1 end", port=1884)

  time.sleep(30)
  mclient.stop()
    """

    # aclient = MQTTSNclient.Client("linh")
    # aclient.registerCallback(MQTTSNclient.Callback())
    # aclient.connect()
    #
    # rc, topic1 = aclient.subscribe("topic1")
    # print("topic id for topic1 is", topic1)
    # topic2 = aclient.subscribe("topic2")
    # print("topic id for topic2 is", topic2)
    # aclient.publish(topic1, "aaaa", qos=0)
    # aclient.publish(topic2, "bbbb", qos=0)
    # aclient.unsubscribe("topic1")
    # aclient.publish(topic2, "bbbb", qos=0)
    # aclient.publish(topic1, "aaaa", qos=0)
    # aclient.disconnect()