import os
import qrcode

# define path to save the QR code images
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "static", "qrcodes")

def generate_qr_code(data: str, filename: str = None) -> str:
    """
    Generates a QR code for the given string and saves it as an PNG file.
    
    :param data: The string to encode in the QR code.
    :param filename: Optional filename for the saved QR code image. If not provided, a default name will be used.
    :return: The path to the saved QR code image.
    """
    # Ensure the output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Create a QR code instance
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    
    # Add data to the QR code
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill_color="black", back_color="white")

    # Determine the filename
    if not filename:
        filename = f"{data}.png"
    
    # Create the full path for the output file
    output_path = os.path.join(OUTPUT_DIR, filename)

    # Save the image
    img.save(output_path)
    print(f"QR code saved to {output_path}")

    return output_path

def generate_qr_for_all_kisten(db_session):
    """
    Generates QR codes for all Kiste entries in the database.
    
    :param db: The database session.
    """
    import crud  # Importing here to avoid circular imports

    kisten = crud.get_all_kisten(db_session)

    if not kisten:
        print("No box entries found in the database.")
        return

    for kiste in kisten:
        qr_code_id = kiste.qr_code_id
        filename = f"{qr_code_id}.png"
        generate_qr_code(data=qr_code_id, filename=filename)

if __name__ == "__main__":
    # text run: create singe QR code for testing
    generate_qr_code("Test QR Code", "test_qr.png")
