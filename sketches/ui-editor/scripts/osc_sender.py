# import json
import logging #,socket

try:
    # import OSC
    from pythonosc.osc_message_builder import OscMessageBuilder
    from pythonosc.udp_client import UDPClient
except ImportError as e:
    # logging.getLogger().warning("Could not import pyOSC library for OscSender:")
    # logging.getLogger().warning(e)
    logging.getLogger().warning("Could not import pythonosc library for OscSender")

class OscSender:
    def __init__(self, host='127.0.0.1', port=8080):
        # attributes
        self.client = None
        self.connected = False

        self.host = host
        self.port = port

        # events
        #self.connectEvent = Event()
        #self.disconnectEvent = Event()

        # configuration
        self.options = {}
        self.configure(options)

    def __del__(self):
        self.destroy()

    def setup(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self._connect()

    def destroy(self):
        self._disconnect()

    def port(self):
        # default is 8080
        return int(self.options['port']) if 'port' in self.options else 8080

    def _connect(self):
        try:
            # self.client = OSC.OSCClient()
            # self.client.connect((self.host(), self.port()))
            # if self.host().endswith('.255'):
            #     logging.getLogger().warn("OSC broadcast destination detected")
            #     self.client.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

            self.client = UDPClient(host, port)
            # sndbufsize = 4096 * 8
            # self.client._sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, sndbufsize)
            # self.client._sock.connect((self.host(), self.port()))
            #
            # if self.host().endswith('.255'):
            #     logging.getLogger().warn("OSC broadcast destination detected")
            #     self.client._sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        except Exception as err: #OSC.OSCClientError as err:
            logging.getLogger().error("OSC connection failure: {0}".format(err))
            return False

        self.connected = True
        logging.getLogger().info("OSC client connected to " + self.host + ':' + str(self.port)
        # self.connectEvent(self)
        return True

    def _disconnect(self):
        if self.client:
            # self.client.close()
            self.client = None
            self.connected = False
            logging.getLogger().info("OSC client closed")
            # self.disconnectEvent(self)

    def send(self, addr, params = []):
        # msg = OSC.OSCMessage()
        # msg.setAddress(tag) # set OSC address
        # for param in params:
        #     msg.append(param)

        msg = OscMessageBuilder(address = addr)
        for param in params:
            msg.add_arg(param)
        msg = msg.build()

        try:
            self.client.send(msg)
            logging.getLogger().debug("OscSender.send " + addr)
        except Exception as err: # OSC.OSCClientError as err:
            logging.getLogger().error("OscSender.send " + addr + " FAILED: " + err)
            pass
            # ColorTerminal().warn("OSC failure: {0}".format(err))
            # no need to call connect again on the client, it will automatically
            # try to connect when we send the next message
