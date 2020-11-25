#!/usr/bin/env python3

import os
import sys

if sys.version_info[0] != 3:
    print("This script requires Python 3")
    exit(1)

if 'py-json' not in sys.path:
    sys.path.append(os.path.join(os.path.abspath('..'), 'py-json'))

import argparse
from LANforge.lfcli_base import LFCliBase
import time
from uuid import uuid1
import pprint
from pprint import pprint

class TestStatusMessage(LFCliBase):
    def __init__(self, host, port,
                 _debug_on=False,
                 _exit_on_error=False,
                 _exit_on_fail=False):
        super().__init__(host, port, _debug=_debug_on, _halt_on_error=_exit_on_error, _exit_on_fail=_exit_on_fail)
        self.check_connect()


    def build(self):
        """create a new session"""
        new_session = uuid1()
        self.status_msg_url = "/status-msg"
        self.session_url = "/status-msg/"+str(new_session)
        # print("----- ----- ----- ----- ----- PUT ----- ----- ----- ----- ----- ----- ")
        self.json_put(self.session_url, _data={})

        # we should see list of sessions
        try:
            #print("----- ----- ----- ----- ----- GET ----- ----- ----- ----- ----- ----- ")
            session_response = self.json_get(self.status_msg_url)
            if self.debug:
                pprint(session_response)
            if "sessions" not in session_response:
                print("----- ----- ----- ----- ----- BAD ----- ----- ----- ----- ----- ----- ")
                self._fail("response lacks sessions element")
            if len(session_response["sessions"]) < 2:
                self._fail("why do we have less than two sessions?")
            for session in session_response["sessions"]:
                #print("----- ----- ----- ----- ----- SESSION ----- ----- ----- ----- ----- ----- ")
                pprint(session)
            self._pass("session created")
        except ValueError as ve:
            print("----- ----- ----- ----- ----- what??? ----- ----- ----- ----- ----- ----- ")
            self._fail(ve)


    def start(self, print_pass=False, print_fail=False):
        """
        create a series of messages
        :return: None
        """
        #print("----- ----- ----- ----- ----- START ----- %s ----- ----- ----- ----- ----- " % self.session_url)
        message_response = self.json_get(self.session_url)
        if self.debug:
            pprint(message_response)
        if "empty" in message_response:
            self._pass("empty response, zero messages")
        elif "messages" in message_response:
            messages_a = message_response["messages"]
            if len(messages_a) > 0:
                self._fail("we should have zero messages")


        for msg_num in ( 1, 2, 3, 4, 5 ):
            #print("----- ----- ----- ----- ----- ----- %s ----- ----- ----- ----- ----- " % msg_num)
            #print("session url: "+self.session_url)
            self.json_post(self.session_url, {
                "key": "test_status_message.py",
                "content-type":"application/json",
                "message":"message %s"%msg_num
            })
            message_response = self.json_get(self.session_url)
            if len(message_response["messages"]) != msg_num:
                pprint(message_response)
                self._fail("we should have %s messages"%msg_num)

        self._pass("created and listed %s messages counted"%msg_num)

    def stop(self):
        """
        make sure we read those messages
        :return: None
        """
        message_response = self.json_get(self.session_url)
        if "empty" in message_response:
            self._fail("empty response, we expect 1 or more messages")
        for message_o in message_response["messages"]:
            msg_url = message_o["_links"]
            print("Message url: "+msg_url)

    def cleanup(self):
        """delete messages and delete the session"""
        self._fail("TODO")
        pass

def main():
    lfjson_port = 8080
    parser = LFCliBase.create_bare_argparse(
        prog=__file__,
        # formatter_class=argparse.RawDescriptionHelpFormatter,
        formatter_class=argparse.RawTextHelpFormatter,

        description="""
Test the status message passing functions of /status-msg:
- create a session: PUT /status-msg/<new-session-id>
- post message: POST /status-msg/<new-session-id>
- list sessions: GET /status-msg/
- list messages for session: GET /status-msg/<new-session-id>
- delete message: DELETE /status-msg/<new-session-id>/message-id
- delete session: DELETE /status-msg/<new-session-id>/this
- delete all messages in session: DELETE /status-msg/<new-session-id>/all
""")
    parser.add_argument('--new', help='create new session')
    parser.add_argument('--update', help='add message to session')
    parser.add_argument('--read', help='read message(s) from session')
    parser.add_argument('--list', help='list messages from session')
    parser.add_argument('--delete', help='delete message')
    args = parser.parse_args()

    status_messages = TestStatusMessage(args.mgr,
                                        lfjson_port,
                                        _debug_on=True,
                                        _exit_on_error=True,
                                        _exit_on_fail=True)
    status_messages.build()
    if not status_messages.passes():
        print(status_messages.get_fail_message())
        exit(1)
    status_messages.start(False, False)
    status_messages.stop()
    if not status_messages.passes():
        print(status_messages.get_fail_message())
        exit(1)
    status_messages.cleanup()
    if status_messages.passes():
        print("Full test passed, all messages read and cleaned up")


if __name__ == "__main__":
    main()
