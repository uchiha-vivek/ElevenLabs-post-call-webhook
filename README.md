**POST CALL TRANSCRIPT WEBHOOK**

This project is flask based webhook receiver that listens for post-call transcripts and automatically triggers the transcript to a specified address.


The following are the steps followed in pipeline:

- Secure webhook validation with HMAC signature verification
- Extracts the call transcript from the webhook payload
- Sends an email notification with the transcript
- Configurable via environment variables

