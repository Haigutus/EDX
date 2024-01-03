#-------------------------------------------------------------------------------
# Name:        EDX_client
# Purpose:
#
# Author:      kristjan.vilgo
#
# Created:     27.03.2018
# Copyright:   (c) kristjan.vilgo 2018
# Licence:     GPL2
#-------------------------------------------------------------------------------
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client as SOAPClient
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from lxml import etree

import urllib3
urllib3.disable_warnings()

# TODO - add logging

class Client:
    """
    This class is designed to create a client for interacting with an EDX MADES SOAP web service.

    The client is initialized with a server address and optional parameters for authentication,
    debugging, SSL verification, and WS-Security. It sets up a session with the server and
    configures the client for the specified web service using WSDL (Web Services Description Language).

    Attributes:
        service: The raw SOAP service object which can be used to make requests to the web service, should not be used as methods in this class already expose all webservice functions.
        history: If debugging is enabled, this attribute stores the history of transactions.
        debug: Boolean flag to enable or disable debugging.

    Args:
        server (str): The server address or IP where the web service is hosted. This parameter is mandatory.
        username (str, optional): The username for HTTP basic authentication. Defaults to None.
        password (str, optional): The password for HTTP basic authentication. Defaults to None.
        debug (bool, optional): Flag to enable or disable debugging features. Defaults to False.
        verify (bool/str, optional): Flag to enable SSL verification or a path to a CA_BUNDLE file or directory with certificates. Defaults to False.
        auth (requests.auth.AuthBase, optional): Custom HTTP authentication mechanism. Any auth supported by "requests.auth" can be used. Defaults to None.
        wsse (zeep.wsse.WSSE, optional): Web Service Security object to add security tokens to SOAP messages. Defaults to None.

    Methods:
        _print_last_message_exchange: Prints the last sent and received SOAP messages. Works only if debug mode is enabled.
        connectivity_test: Performs a connectivity test with the given receiver EIC and business type. Returns a message ID.
        send_message: Sends a message to the specified receiver with given parameters. Returns a message ID.
        check_message_status: Checks the status of a message using its message ID. Returns the status of the message.
        receive_message: Receives a message of a specified business type. Returns the received message and the remaining message count.
        confirm_received_message: Confirms the receipt of a message using its message ID. Returns the same message ID as confirmation.

    Notes:
        - If 'username' is provided, HTTP basic authentication is set up with 'username' and 'password' and will perform preemptive auth.
        - If 'auth' is provided, it is used as the authentication mechanism.
        - If 'wsse' is provided, it will be used to add security tokens to the SOAP messages, enabling WS-Security.
        - Enabling 'debug' logs detailed information about the raw SOAP requests and responses.
    """

    def __init__(self, server, username=None, password=None, debug=False, verify=False, auth=None, wsse=None):

        """At minimum server address or IP must be provided"""

        wsdl = f'{server}/ws/madesInWSInterface.wsdl'

        # Authenticate HTTP session
        session = Session()
        session.verify = verify

        if username:
            session.auth = HTTPBasicAuth(username, password)
            session.get(wsdl)  # Preemptive auth, needed for keycloak

        if auth:
            session.auth = auth

        transport = Transport(session=session)

        # Add history plugin for debug
        self.history = HistoryPlugin()
        self.debug = debug

        plugins = []

        if debug:
            plugins.append(self.history)

        # Create SOAP client
        client = SOAPClient(wsdl, transport=transport, plugins=plugins, wsse=wsse)

        self.service = client.create_service(
            binding_name='{http://mades.entsoe.eu/}MadesEndpointSOAP12',
            address=f'{server}/ws/madesInWSInterface')

    def _print_last_message_exchange(self):
        """Prints out last sent and received SOAP messages"""

        if not self.debug:
            print("WARNING - debug mode must be enabled for function _print_last_message_exchange to work")
            return

        messages = {"SENT":     self.history.last_sent,
                    "RECEIVED": self.history.last_received}
        print("-" * 50)

        for message in messages:

            print(f"### {message} HTTP HEADER ###")
            print('\n' * 1)
            print(messages[message]["http_headers"])
            print('\n' * 1)
            print(f"### {message} HTTP ENVELOPE START ###")
            print('\n' * 1)
            print(etree.tostring(messages[message]["envelope"], pretty_print=True).decode())
            print(f"### {message} HTTP ENVELOPE END ###")
            print('\n' * 1)

        print("-" * 50)

    def connectivity_test(self, reciver_EIC, business_type):
        """ConnectivityTest(receiverCode: xsd:string, businessType: xsd:string) -> messageID: xsd:string"""

        message_id = self.service.ConnectivityTest(reciver_EIC, business_type)

        return message_id

    def send_message(self, receiver_EIC, business_type, content, sender_EIC="", ba_message_id="", conversation_id=""):
        """SendMessage(message: ns0:SentMessage, conversationID: xsd:string) -> messageID: xsd:string
           ns0:SentMessage(receiverCode: xsd:string, businessType: xsd:string, content: xsd:base64Binary, senderApplication: xsd:string, baMessageID: xsd:string)"""

        message_dic = {"receiverCode": receiver_EIC, "businessType": business_type, "content": content, "senderApplication": sender_EIC, "baMessageID": ba_message_id}
        message_id  = self.service.SendMessage(message_dic, conversation_id)

        return message_id

    def check_message_status(self, message_id):
        """CheckMessageStatus(messageID: xsd:string) -> messageStatus: ns0:MessageStatus
           ns0:MessageStatus(messageID: xsd:string, state: ns0:MessageState, receiverCode: xsd:string, senderCode: xsd:string, businessType: xsd:string, senderApplication: xsd:string, baMessageID: xsd:string, sendTimestamp: xsd:dateTime, receiveTimestamp: xsd:dateTime, trace: ns0:MessageTrace)"""

        status = self.service.CheckMessageStatus(message_id)

        return status

    def receive_message(self, business_type="*", download_message=True, auto_confirm=False):
        """ReceiveMessage(businessType: xsd:string, downloadMessage: xsd:boolean) -> receivedMessage: ns0:ReceivedMessage, remainingMessagesCount: xsd:long"""

        received_message = self.service.ReceiveMessage(business_type, download_message)

        if auto_confirm:
            self.confirm_received_message(received_message.receivedMessage.messageID)

        return received_message

    def confirm_received_message(self, message_id):
        """ConfirmReceiveMessage(messageID: xsd:string) -> messageID: xsd:string"""

        message_id = self.service.ConfirmReceiveMessage(message_id)

        return message_id


# Deprecated class name
create_client = Client


# TEST

if __name__ == '__main__':

    server = "https://er-opde-acceptance.elering.sise"
    username = input("UserName")
    password = input("PassWord")

    service = Client(server, username, password)

    # Send message example

    file_path = "C:/Users/kristjan.vilgo/Downloads/13681847.xml"

    with open(file_path, "rb") as loaded_file:
        message_ID = service.send_message("10V000000000011Q", "RIMD", loaded_file.read())

    print(service.check_message_status(message_ID))

    # Retrieve message example

    message = service.receive_message("RIMD")
    print(message)
    #service.confirm_received_message(message.receivedMessage.messageID)


# SERVICE DESCRIPTION

##Operations:
##    CheckMessageStatus(messageID: xsd:string) -> messageStatus: ns0:MessageStatus
##    ConfirmReceiveMessage(messageID: xsd:string) -> messageID: xsd:string
##    ConnectivityTest(receiverCode: xsd:string, businessType: xsd:string) -> messageID: xsd:string
##    ReceiveMessage(businessType: xsd:string, downloadMessage: xsd:boolean) -> receivedMessage: ns0:ReceivedMessage, remainingMessagesCount: xsd:long
##    SendMessage(message: ns0:SentMessage, conversationID: xsd:string) -> messageID: xsd:string

##Global elements:
##     ns0:CheckMessageStatusError(errorCode: xsd:string, errorID: xsd:string, errorMessage: xsd:string, messageID: xsd:string, errorDetails: xsd:string)
##     ns0:CheckMessageStatusRequest(messageID: xsd:string)
##     ns0:CheckMessageStatusResponse(messageStatus: ns0:MessageStatus)
##     ns0:ConfirmReceiveMessageError(errorCode: xsd:string, errorID: xsd:string, errorMessage: xsd:string, messageID: xsd:string, errorDetails: xsd:string)
##     ns0:ConfirmReceiveMessageRequest(messageID: xsd:string)
##     ns0:ConfirmReceiveMessageResponse(messageID: xsd:string)
##     ns0:ConnectivityTestError(errorCode: xsd:string, errorID: xsd:string, errorMessage: xsd:string, receiverCode: xsd:string, errorDetails: xsd:string)
##     ns0:ConnectivityTestRequest(receiverCode: xsd:string, businessType: xsd:string)
##     ns0:ConnectivityTestResponse(messageID: xsd:string)
##     ns0:ReceiveMessageError(errorCode: xsd:string, errorID: xsd:string, errorMessage: xsd:string, businessType: xsd:string, errorDetails: xsd:string)
##     ns0:ReceiveMessageRequest(businessType: xsd:string, downloadMessage: xsd:boolean)
##     ns0:ReceiveMessageResponse(receivedMessage: ns0:ReceivedMessage, remainingMessagesCount: xsd:long)
##     ns0:SendMessageError(errorCode: xsd:string, errorID: xsd:string, errorMessage: xsd:string, receiverCode: xsd:string, errorDetails: xsd:string)
##     ns0:SendMessageRequest(message: ns0:SentMessage, conversationID: xsd:string)
##     ns0:SendMessageResponse(messageID: xsd:string)
##
##
##Global types:
##
##     ns0:MessageState
##     ns0:MessageStatus(messageID: xsd:string, state: ns0:MessageState, receiverCode: xsd:string, senderCode: xsd:string, businessType: xsd:string, senderApplication: xsd:string, baMessageID: xsd:string, sendTimestamp: xsd:dateTime, receiveTimestamp: xsd:dateTime, trace: ns0:MessageTrace)
##     ns0:MessageTrace(trace: ns0:MessageTraceItem[])
##     ns0:MessageTraceItem(timestamp: xsd:dateTime, state: ns0:MessageTraceState, component: xsd:string, componentDescription: xsd:string, details: xsd:string)
##     ns0:MessageTraceState
##     ns0:ReceivedMessage(messageID: xsd:string, receiverCode: xsd:string, senderCode: xsd:string, businessType: xsd:string, content: xsd:base64Binary, senderApplication: xsd:string, baMessageID: xsd:string)
##     ns0:SentMessage(receiverCode: xsd:string, businessType: xsd:string, content: xsd:base64Binary, senderApplication: xsd:string, baMessageID: xsd:string)
