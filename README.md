# EDX
Python implementation of EDX SOAP MADES API (ENTSO-E Data Exchange Software - https://www.entsoe.eu/data/edx/) 

# Installation

    pip install EDX

or

    pip install --user EDX

or 

    python -m pip install --user EDX


# Usage

### Initialise
    import EDX

    service = EDX.create_client("https://edx.elering.sise")

### Send message
    with open("message.xml", "rb") as loaded_file:
        message_ID = service.send_message("10V000000000011Q", "RIMD", loaded_file.read())

### Check message status
    status = service.check_message_status(message_ID)

### Retrieve message
    message = service.receive_message()
    
### Confirm retrieval of message
    service.confirm_received_message(message.receivedMessage.messageID)
    
### Save message on drive
*in case of excel use .xlsx and in case of PDF use .pdf and etc*

    with open("report.xml", 'wb') as report_file:
        report_file.write(message.receivedMessage.content)
        
### Save message as file like object in memory

    file_like_object = io.BytesIO(message.receivedMessage.content)

    
    
