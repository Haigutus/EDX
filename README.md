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
    message_ID = service.send_message("10V000000000011Q", "RIMD", "C:/Users/kristjan.vilgo/Desktop/13681847.xml", "38V-EE-OPDM----S", "", "")

    # Check message status
    status = service.check_message_status(message_ID)

    # Retrive message
    message = service.recieve_message("RIMD",1)
    
    # Confirm retrival of message
    service.confirm_recieved_message(message["receivedMessage"]["messageID"])
