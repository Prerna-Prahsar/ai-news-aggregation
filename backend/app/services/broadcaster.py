import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional, Dict
from app.core.config import settings

logger = logging.getLogger(__name__)


def build_email_html(title: str, summary: str, url: str, source: str) -> str:
    return f"""
    <html><body style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
      <div style="background: #1e293b; padding: 20px; border-radius: 8px 8px 0 0;">
        <h1 style="color: #38bdf8; font-size: 18px; margin: 0;">🤖 AI News Update</h1>
      </div>
      <div style="background: #f8fafc; padding: 20px; border: 1px solid #e2e8f0;">
        <h2 style="color: #0f172a; font-size: 16px;">{title}</h2>
        <p style="color: #64748b; font-size: 14px;">{summary or 'No summary available.'}</p>
        <p style="font-size: 12px; color: #94a3b8;">Source: {source}</p>
        <a href="{url}" style="display:inline-block; background:#3b82f6; color:white;
           padding:10px 20px; border-radius:6px; text-decoration:none; font-size:14px;">
          Read Full Article →
        </a>
      </div>
    </body></html>
    """


def send_email(recipients: List[str], subject: str, title: str,
               summary: str, url: str, source: str = "") -> Dict:
    if not settings.SMTP_USER or not settings.SMTP_PASS:
        return {
            "status": "simulated",
            "message": f"Email simulated to {', '.join(recipients)}. Configure SMTP_USER/SMTP_PASS for real emails.",
        }
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = settings.SMTP_USER
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(build_email_html(title, summary, url, source), "html"))
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.sendmail(settings.SMTP_USER, recipients, msg.as_string())
        return {"status": "sent", "message": f"Email sent to {', '.join(recipients)}"}
    except Exception as e:
        return {"status": "failed", "message": str(e)}


def generate_linkedin_caption(title: str, summary: str, url: str) -> str:
    snippet = (summary or "")[:200]
    return (
        f"🚀 Exciting AI Development!\n\n"
        f"📰 {title}\n\n"
        f"{snippet}...\n\n"
        f"Read more: {url}\n\n"
        f"#ArtificialIntelligence #MachineLearning #AI #Tech #Innovation"
    )


def post_to_linkedin(title: str, summary: str, url: str) -> Dict:
    caption = generate_linkedin_caption(title, summary, url)
    return {
        "status": "simulated",
        "message": caption,
    }


def send_whatsapp(recipients: List[str], title: str, url: str, summary: str) -> Dict:
    msg = f"🤖 *AI News Alert*\n\n*{title}*\n\n{(summary or '')[:200]}...\n\n🔗 {url}"
    return {
        "status": "simulated",
        "message": f"WhatsApp message simulated for {len(recipients)} recipient(s).",
        "preview": msg,
    }


def add_to_blog(title: str, summary: str, url: str) -> Dict:
    return {
        "status": "simulated",
        "message": "Blog post draft created. Integrate with your CMS to publish.",
        "draft": {"title": f"[AI News] {title}", "content": summary, "source_url": url},
    }


def add_to_newsletter(title: str, summary: str, url: str, author: str = "") -> Dict:
    return {
        "status": "simulated",
        "message": "Added to newsletter queue. Integrate with Mailchimp/Beehiiv to send.",
    }


def broadcast(platform: str, title: str, summary: str, url: str,
              source: str = "", author: str = "",
              recipients: Optional[List[str]] = None) -> Dict:
    recipients = recipients or []
    if platform == "email":
        return send_email(recipients, f"AI News: {title[:80]}", title, summary, url, source)
    elif platform == "linkedin":
        return post_to_linkedin(title, summary, url)
    elif platform == "whatsapp":
        return send_whatsapp(recipients, title, url, summary)
    elif platform == "blog":
        return add_to_blog(title, summary, url)
    elif platform == "newsletter":
        return add_to_newsletter(title, summary, url, author)
    return {"status": "failed", "message": f"Unknown platform: {platform}"}