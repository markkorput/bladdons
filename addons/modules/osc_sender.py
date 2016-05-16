
# import json
import logging

try:
    # import OSC
    from pythonosc.osc_message_builder import OscMessageBuilder
    from pythonosc.udp_client import UDPClient
except ImportError:
    # logging.getLogger().warning("importing embedded version of pyOSC library for OscWriter")
    # import local.OSC as OSC
    logging.getLogger().warning("Could not import pythonosc library for OscSender")
    # from pythonosc.osc_message_builder import OscMessageBuilder
    # from pythonosc.udp_client import UDPClient

class OscSender:
    def __init__(self, options = {}):
        # attributes
        self.client = None
        self.running = False
        self.connected = False

        # events
        #self.connectEvent = Event()
        #self.disconnectEvent = Event()

        # configuration
        self.options = {}
        self.configure(options)

    def __del__(self):
        self.destroy()

    def configure(self, options):
        # we might need the overwritten options
        previous_options = self.options
        # overwrite/update configuration
        self.options.update(options)

        # new host or port configs? We need to reconnect, but only if we're running
        if ('host' in options or 'port' in options) and self.running:
            self.destroy()
            self.setup()

    def setup(self):
        if self._connect():
            self.running = True

    def destroy(self):
        self._disconnect()
        self.running = False

    def port(self):
        # default is 8080
        return int(self.options['port']) if 'port' in self.options else 8080

    def host(self):
        # default is localhost
        return self.options['host'] if 'host' in self.options else '127.0.0.1'

    def _connect(self):
        try:
            # self.client = OSC.OSCClient()
            # self.client.connect((self.host(), self.port()))
            self.client = UDPClient(self.host(), self.port())
        except Exception as err: #OSC.OSCClientError as err:
            logging.getLogger().error("OSC connection failure: {0}".format(err))
            return False

        self.connected = True
        logging.getLogger().info("OSC client connected to " + self.host() + ':' + str(self.port()))
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
