import os
import ssl
import hmac
import hashlib
import smtplib
from flask import Flask, request, json
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Environment variables
HMAC_SECRET = os.getenv("HMAC_SECRET")  
SMTP_EMAIL = os.getenv("SMTP_EMAIL")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

if not HMAC_SECRET:
    raise ValueError("HMAC_SECRET not found in environment variables!")

HMAC_SECRET = HMAC_SECRET.encode("utf-8")


# ---------------- HMAC SIGNATURE VERIFICATION ---------------- #
def verify_signature(req):
    signature_header = req.headers.get("Elevenlabs-Signature")
    if not signature_header:
        print("Missing signature headers")
        return False

    try:
        parts = dict(item.split("=", 1) for item in signature_header.split(","))
        timestamp = parts["t"]
        signature = parts["v0"]
    except Exception:
        print("Malformed signature header")
        return False

    signed_payload = f"{timestamp}.{req.data.decode('utf-8')}".encode()
    expected_sig = hmac.new(HMAC_SECRET, signed_payload, hashlib.sha256).hexdigest()

    return hmac.compare_digest(signature, expected_sig)


# ---------------- EMAIL SENDER ---------------- #
def send_email(transcript):
    try:
        msg = EmailMessage()
        msg["From"] = SMTP_EMAIL
        msg["To"] = os.getenv("RECIPIENT_EMAIL")  
        msg["Subject"] = "New Call Transcript"
        msg.set_content(
            f"Hello,\n\n"
            f"A new call transcript has been received:\n\n"
            f"{transcript}\n\n"
            f"Best regards,\nYour System"
        )

        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(SMTP_EMAIL, SMTP_PASSWORD)
            server.send_message(msg)

        print("Email sent with transcript")
    except Exception as e:
        print(f"Email sending failed: {e}")


# ---------------- WEBHOOK HANDLER ---------------- #
@app.route("/post-call-support", methods=["POST"])
def handle_support_call():
    if not verify_signature(request):
        return "Missing or invalid signature", 403

    call_data = request.get_json(silent=True) or {}
    print("Incoming webhook:", json.dumps(call_data, indent=2))

    transcript = call_data.get("data", {}).get("transcript", "No transcript provided")

    send_email(transcript)

    return "OK", 200



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
