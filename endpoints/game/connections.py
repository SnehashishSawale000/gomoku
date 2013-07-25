# -*- coding: utf-8 -*-

from sockjs.tornado import SockJSConnection


class MultiParticipantsConnection(SockJSConnection):
    """Connection, which save participants and support additional
    methods for working with participants."""
    participants = set()

    def on_open(self, info):
        self.participants.add(self)
        super().on_open(info)

    def broadcast_all(self, message):
        """Broadcast message to all participants."""
        target_class = self.__class__
        targets = [i for i in self.participants if isinstance(i, target_class)]
        self.broadcast(targets, message)


class ChannelConnection(SockJSConnection):
    """Connection, for working with multiplex channels."""
    def send_channel(self, channel, message, binary=False):
        """Send message to the specific channel."""
        if not self.is_closed:
            self.session.send_message_channel(channel, message, binary=binary)

    def broadcast_channel(self, channel, clients, message):
        """Broadcast message to some participants for the specific
        channel."""
        self.session.broadcast_channel(channel, clients, message)

    def broadcast_all_channel(self, channel, message):
        """Broadcast message to all participants for the specific
        channel. This method expects, that `participants` property is
        already exists (using, for example, `MultiParticipantsConnection`).
        """
        target_class = self.__class__
        targets = [i for i in self.participants if isinstance(i, target_class)]
        self.session.broadcast_channel(channel, targets, message)