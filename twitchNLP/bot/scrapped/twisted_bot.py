"""
twisted_bot.py - Connects to an IRC and logs chat using twisted library.
msimo - 2/6/15 - VTHacksII
Python 2.7.6
Modified version of ircLogBot provided by TwistedMatrix
"""

#Standard Libraries
import time
import sys

#Third-party Libraries
from twisted.words.protocols import irc
from twisted.internet import reactor, protocol
from twisted.python import log

class MessageLogger:
    """
    An independent logger class (because separation of application
    and protocol logic is a good thing).
    """
    def __init__(self, file):
        self.file = file

    def log(self, message):
        """Write a message to the file."""
        timestamp = time.strftime("[%H:%M:%S]", time.localtime(time.time()))
        self.file.write('%s %s\n' % (timestamp, message))
        self.file.flush()

    def close(self):
        self.file.close()


class LogBot(irc.IRCClient):
    """A logging IRC bot."""
    
    nickname = "darkiee"
    password = "oauth:redacted"
    
    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        self.logger = MessageLogger(open(self.factory.filename, "a"))
        self.logger.log("[connected at {}]".format(time.asctime(time.localtime(time.time()))))

    def connectionLost(self, reason):
        irc.IRCClient.connectionLost(self, reason)
        self.logger.log("[disconnected at {}]".format(time.asctime(time.localtime(time.time()))))
        self.logger.close()

    # callbacks for events
    def signedOn(self):
        """Called when bot has succesfully signed on to server."""
        self.join(self.factory.channel)

    def joined(self, channel):
        """This will get called when the bot joins the channel."""
        self.logger.log("[I have joined %s]" % channel)

    def privmsg(self, user, channel, msg):
        """This will get called when the bot receives a message."""
        user = user.split('!', 1)[0]
        self.logger.log("<%s> %s" % (user, msg))
        
        # Check to see if they're sending me a private message
        if channel == self.nickname:
            msg = "It isn't nice to whisper!  Play nice with the group."
            self.msg(user, msg)
            return

        # Otherwise check to see if it is a message directed at me
        if msg.startswith(self.nickname + ":"):
            msg = "%s: I am a log bot" % user
            self.msg(channel, msg)
            self.logger.log("<%s> %s" % (self.nickname, msg))

    def action(self, user, channel, msg):
        """This will get called when the bot sees someone do an action."""
        user = user.split('!', 1)[0]
        self.logger.log("* %s %s" % (user, msg))

    # irc callbacks
    def irc_NICK(self, prefix, params):
        """Called when an IRC user changes their nickname."""
        old_nick = prefix.split('!')[0]
        new_nick = params[0]
        self.logger.log("%s is now known as %s" % (old_nick, new_nick))

    # For fun, override the method that determines how a nickname is changed on
    # collisions. The default method appends an underscore.
    def alterCollidedNick(self, nickname):
        """
        Generate an altered version of a nickname that caused a collision in an
        effort to create an unused related name for subsequent registration.
        """
        return nickname + '^'

class LogBotFactory(protocol.ClientFactory):
    """A factory for LogBots.

    A new protocol instance will be created each time we connect to the server.
    """

    def __init__(self, username, password, channel, filename):
        self.username = username
        self.password = password
        self.channel = channel
        self.filename = filename

    def buildProtocol(self, addr):
        p = LogBot()
        p.factory = self
        return p

    def clientConnectionLost(self, connector, reason):
        """If we get disconnected, reconnect to server."""
        connector.connect()

    def clientConnectionFailed(self, connector, reason):
        print "connection failed:", reason
        reactor.stop()

def create_logger(username, password, server, port, channel, logfile):
	# initialize logging
    log.startLogging(sys.stdout)
    
    # create factory protocol and application
    f = LogBotFactory(username, password, channel, logfile)

    # connect factory to this host and port
    reactor.connectTCP(server, port, f)

    # run bot
    reactor.run()

def main():
    create_logger("Darkiee", "oauth:4j4rjtpndj59vdhmmcnsodk03uppuc", "irc.twitch.tv", 6667, "MANvsGAME", "mvg.log")

if __name__ == '__main__':
	main()
