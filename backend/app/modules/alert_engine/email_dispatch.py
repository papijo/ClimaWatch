import resend

from app.config import settings

resend.api_key = settings.RESEND_API_KEY

SENDER = "ClimaWatch Alerts <hello@weareserge.com>"


def send_alert_email(
    to_email: str,
    state_name: str,
    risk_level: str,
    advisory: str,
) -> str:
    subject = f"[ClimaWatch] {risk_level} Climate-Health Alert — {state_name}"
    html = f"""
    <h2>ClimaWatch Alert: {state_name} State</h2>
    <p><strong>Risk Level:</strong> {risk_level}</p>
    <p>{advisory}</p>
    <hr>
    <p style="font-size:12px;color:#666;">
      You received this because you subscribed to alerts for {state_name} on ClimaWatch.
      Visit <a href="https://climawatch.ng">climawatch.ng</a> to manage your preferences.
    </p>
    """
    response = resend.Emails.send({
        "from": SENDER,
        "to": [to_email],
        "subject": subject,
        "html": html,
    })
    return response["id"]
