import io
import qrcode
from qrcode.image.pil import PilImage


def generate_qr_code(data: str) -> bytes:
    """
    Generate a QR code PNG image for the given data string.
    Returns the image as raw bytes.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img: PilImage = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def generate_distribution_qr(distribution_id: str, beneficiary_id: str, ration_type: str) -> bytes:
    """
    Generate a QR code for a specific distribution acknowledgement.
    Encodes key distribution metadata as a URL-safe payload.
    """
    payload = f"dist:{distribution_id}|ben:{beneficiary_id}|type:{ration_type}"
    return generate_qr_code(payload)
