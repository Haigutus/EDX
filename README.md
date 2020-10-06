# EDX
Python implementation of EDX SOAP API (ENTSO-E Data Exchange Software - https://www.entsoe.eu/data/edx/) 

# Installation

    pip install EDX

or

    pip install --user EDX

or 

    python -m pip install --user EDX


# Usage

    import EDX


    service = EDX.create_client("https://edx.elering.sise")

    # Send message

    file_path   = "C:/Users/kristjan.vilgo/Desktop/13681847.xml"
    loaded_file = open(file_path, "rb")
    file_text   = loaded_file.read()
    
    loaded_file.close()

    message_ID = service.send_message("10V000000000011Q", "RIMD", file_text)

    # Check message status
    status = service.check_message_status(message_ID)

    # Retrieve message
    message = service.receive_message()
    
    # Confirm retrieval of message
    service.confirm_received_message(message.receivedMessage.messageID)
    
    # Save message on drive    
    file = open("report.xml", 'wb') # in case of excel use .xlsx and in case of PDF use .pdf and etc.

    file.write(message.receivedMessage.content)
    file.close()

    # Save message as file like object in memory

    file_like_object = io.BytesIO(message.receivedMessage.content)

    
    
