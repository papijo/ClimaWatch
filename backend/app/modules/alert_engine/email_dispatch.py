import logging

import resend

from app.config import settings

logger = logging.getLogger(__name__)

resend.api_key = settings.RESEND_API_KEY

SENDER = "ClimaWatch Alerts <hello@weareserge.com>"

RISK_COLORS = {
    "HIGH": "#f97316",
    "CRITICAL": "#ef4444",
    "MODERATE": "#eab308",
}


def build_alert_html(
    state_name: str,
    risk_level: str,
    advisory: str,
    recipient_name: str,
) -> str:
    color = RISK_COLORS.get(risk_level, "#6b7280")
    return f"""\
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family:Arial,Helvetica,sans-serif;margin:0;padding:0;background:#f9fafb;">
  <table width="100%" cellpadding="0" cellspacing="0" style="max-width:600px;margin:0 auto;background:#ffffff;">
    <tr>
      <td style="padding:24px 32px;background:#1e293b;color:#ffffff;">
        <h1 style="margin:0;font-size:20px;">ClimaWatch</h1>
      </td>
    </tr>
    <tr>
      <td style="padding:32px;">
        <p style="margin:0 0 8px;font-size:14px;color:#6b7280;">Hello {recipient_name},</p>
        <h2 style="margin:0 0 16px;font-size:22px;">
          <span style="display:inline-block;padding:4px 12px;border-radius:6px;background:{color};color:#ffffff;font-size:14px;vertical-align:middle;">{risk_level}</span>
          Climate-Health Alert — {state_name} State
        </h2>
        <div style="padding:16px;background:#f1f5f9;border-radius:8px;margin:0 0 24px;">
          <p style="margin:0;font-size:14px;line-height:1.6;color:#334155;">{advisory}</p>
        </div>
        <p style="margin:0;font-size:13px;color:#94a3b8;">
          You received this because you subscribed to alerts for {state_name} on ClimaWatch.
          Visit <a href="https://climawatch.ng/me/subscriptions" style="color:#3b82f6;">climawatch.ng</a> to manage your preferences.
        </p>
      </td>
    </tr>
    <tr>
      <td style="padding:16px 32px;background:#f1f5f9;text-align:center;">
        <p style="margin:0;font-size:12px;color:#94a3b8;">&copy; ClimaWatch by Serge Ltd. All rights reserved.</p>
      </td>
    </tr>
  </table>
</body>
</html>"""


def send_alert_email(
    to_email: str,
    state_name: str,
    risk_level: str,
    advisory: str,
    recipient_name: str = "there",
) -> str | None:
    subject = f"[ClimaWatch] {risk_level} Climate-Health Alert — {state_name}"
    html = build_alert_html(state_name, risk_level, advisory, recipient_name)
    try:
        response = resend.Emails.send({
            "from": SENDER,
            "to": [to_email],
            "subject": subject,
            "html": html,
        })
        logger.info("Email sent to %s (id=%s)", to_email, response["id"])
        return response["id"]
    except Exception:
        logger.exception("Failed to send email to %s", to_email)
        return None


def dispatch_alerts(
    subscribers: list[dict],
    state_name: str,
    risk_level: str,
    advisory: str,
) -> dict[str, int]:
    """Send alert emails to all subscribers. Returns success/failure counts."""
    sent = 0
    failed = 0
    for sub in subscribers:
        result = send_alert_email(
            to_email=sub["email"],
            state_name=state_name,
            risk_level=risk_level,
            advisory=advisory,
            recipient_name=sub.get("full_name", "there"),
        )
        if result:
            sent += 1
        else:
            failed += 1

    logger.info(
        "Alert dispatch for %s (%s): sent=%d, failed=%d",
        state_name, risk_level, sent, failed,
    )
    return {"sent": sent, "failed": failed}
