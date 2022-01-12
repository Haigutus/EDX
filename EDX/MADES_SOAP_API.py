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
from zeep import Client
from zeep.transports import Transport
from zeep.plugins import HistoryPlugin
from lxml import etree

import urllib3
urllib3.disable_warnings()

# TODO - add logging

class create_client():

    def __init__(self, server, username="", password="", debug=False):

        """At minimum server address or IP must be provided"""

        wsdl = '{}/ws/madesInWSInterface.wsdl'.format(server)

        session        = Session()
        session.verify = False
        session.auth   = HTTPBasicAuth(username, password)
        session.get(server)  # Preemptive auth, needed for keycloak

        transport = Transport(session=session)
        self.history = HistoryPlugin()
        self.debug = debug

        if debug:
            client = Client(wsdl, transport=transport, plugins=[self.history])
        else:
            client = Client(wsdl, transport=transport)

        client.debug = debug

        self.service = client.create_service(
            '{http://mades.entsoe.eu/}MadesEndpointSOAP12',
            '{}/ws/madesInWSInterface'.format(server))

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

    def receive_message(self, business_type="*", download_message=True):
        """ReceiveMessage(businessType: xsd:string, downloadMessage: xsd:boolean) -> receivedMessage: ns0:ReceivedMessage, remainingMessagesCount: xsd:long"""

        received_message = self.service.ReceiveMessage(business_type, download_message)

        return received_message

    def confirm_received_message(self, message_id):
        """ConfirmReceiveMessage(messageID: xsd:string) -> messageID: xsd:string"""

        message_id = self.service.ConfirmReceiveMessage(message_id)

        return message_id


# TEST


if __name__ == '__main__':

    server = "https://er-opde-acceptance.elering.sise"
    username = input("UserName")
    password = input("PassWord")

    service = create_client(server, username, password)

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
