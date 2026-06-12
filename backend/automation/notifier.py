# backend/automation/notifier.py
# WHY: Candidates need to know when they match a job.
# Referrers need to know when someone wants their help.
# Email keeps users engaged without them checking the app constantly.

import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

GMAIL_USER = os.getenv("GMAIL_USER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")


def send_email(to_email: str, subject: str, html_body: str):
    """
    WHY: Core email sender — all other functions build on this.
    Uses Gmail SMTP with TLS — free and reliable.
    """
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = to_email
        msg.attach(MIMEText(html_body, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_USER, to_email, msg.as_string())

        print(f"✅ Email sent to {to_email}")
        return True

    except Exception as e:
        print(f"⚠️ Email failed to {to_email}: {e}")
        return False


def notify_candidate_matched(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    company: str,
    match_score: float,
    gap_analysis: dict
):
    """
    WHY: Tell candidate they matched a job with specific details.
    We include the gap analysis so they know exactly what to work on.
    """
    strong_points = "".join([
        f"<li>✅ {point}</li>"
        for point in gap_analysis.get("strong_points", [])
    ])
    missing = "".join([
        f"<li>⚠️ {item}</li>"
        for item in gap_analysis.get("missing_critical", [])
    ])
    action_plan = "".join([
        f"<li><b>{a['action']}</b> — {a['timeline']} via {a['resource']}</li>"
        for a in gap_analysis.get("action_plan", [])
    ])

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
        <div style="background: #6C63FF; padding: 20px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0;">RefNet 🎯</h1>
            <p style="color: #e0e0ff; margin: 5px 0;">Merit-based referrals for everyone</p>
        </div>

        <div style="padding: 24px; background: #f9f9f9;">
            <h2>Hi {candidate_name}, you have a new job match!</h2>

            <div style="background: white; border-radius: 8px; padding: 16px; margin: 16px 0;">
                <h3 style="margin: 0; color: #6C63FF;">{job_title}</h3>
                <p style="margin: 4px 0; color: #666;">{company}</p>
                <div style="background: #6C63FF; color: white; display: inline-block;
                            padding: 4px 12px; border-radius: 20px; margin-top: 8px;">
                    Match Score: {match_score}%
                </div>
            </div>

            <h3>Your Strengths for This Role:</h3>
            <ul>{strong_points}</ul>

            <h3>Gaps to Address:</h3>
            <ul>{missing if missing else '<li>✅ No critical gaps!</li>'}</ul>

            <h3>Your Action Plan:</h3>
            <ul>{action_plan}</ul>

            <div style="background: #6C63FF; color: white; padding: 16px;
                        border-radius: 8px; margin-top: 20px; text-align: center;">
                <p style="margin: 0; font-size: 18px;">
                    Referral Readiness: {gap_analysis.get('referral_readiness', '')}
                </p>
            </div>
        </div>

        <div style="padding: 16px; text-align: center; color: #999; font-size: 12px;">
            RefNet — Skills over connections. Always.
        </div>
    </div>
    """

    return send_email(
        to_email=candidate_email,
        subject=f"🎯 New Match: {job_title} at {company} — {match_score}% fit",
        html_body=html
    )


def notify_referrer_new_candidate(
    referrer_email: str,
    referrer_name: str,
    job_title: str,
    candidate_skills: str,
    match_score: float,
    referral_message: str,
    match_request_id: str
):
    """
    WHY: Tell referrer someone wants their help.
    IMPORTANT: We show skills only — no name, no photo, no gender.
    This is the anonymity layer that makes RefNet safe and fair.
    """
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
        <div style="background: #6C63FF; padding: 20px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0;">RefNet 🤝</h1>
            <p style="color: #e0e0ff; margin: 5px 0;">Someone needs your help</p>
        </div>

        <div style="padding: 24px; background: #f9f9f9;">
            <h2>Hi {referrer_name},</h2>
            <p>A verified candidate is looking for a referral at your company.</p>

            <div style="background: white; border-radius: 8px; padding: 16px; margin: 16px 0;">
                <h3 style="margin: 0; color: #6C63FF;">Role: {job_title}</h3>
                <p><b>Candidate Skills:</b> {candidate_skills}</p>
                <p><b>Match Score:</b> {match_score}%</p>
                <div style="background: #f0f0ff; border-left: 4px solid #6C63FF;
                            padding: 12px; margin-top: 12px; border-radius: 4px;">
                    <p style="margin: 0; font-style: italic;">"{referral_message}"</p>
                </div>
            </div>

            <p style="color: #666; font-size: 14px;">
                ℹ️ Candidate identity is hidden until you accept.
                You're evaluating skills, not a person's name or background.
            </p>

            <div style="text-align: center; margin-top: 20px;">
                <a href="http://localhost:8000/referral/accept/{match_request_id}"
                   style="background: #6C63FF; color: white; padding: 12px 32px;
                          border-radius: 8px; text-decoration: none; margin-right: 10px;">
                    ✅ Accept & Refer
                </a>
                <a href="http://localhost:8000/referral/decline/{match_request_id}"
                   style="background: #eee; color: #333; padding: 12px 32px;
                          border-radius: 8px; text-decoration: none;">
                    ❌ Decline
                </a>
            </div>
        </div>

        <div style="padding: 16px; text-align: center; color: #999; font-size: 12px;">
            RefNet — No DMs. No bias. Just skills.
        </div>
    </div>
    """

    return send_email(
        to_email=referrer_email,
        subject=f"🤝 Referral Request: {job_title} — {match_score}% match candidate",
        html_body=html
    )


def notify_referral_accepted(
    candidate_email: str,
    candidate_name: str,
    job_title: str,
    company: str,
    referrer_name: str
):
    """WHY: Tell candidate their referral was accepted — big moment."""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto;">
        <div style="background: #28a745; padding: 20px; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0;">🎉 Referral Accepted!</h1>
        </div>
        <div style="padding: 24px;">
            <h2>Congratulations {candidate_name}!</h2>
            <p><b>{referrer_name}</b> has agreed to refer you for:</p>
            <h3 style="color: #6C63FF;">{job_title} at {company}</h3>
            <p>They will submit your referral to the company's HR team.</p>
            <p style="color: #666;">
                This happened because of your skills — not your network.
                That's RefNet working exactly as intended. 💪
            </p>
        </div>
    </div>
    """
    return send_email(
        to_email=candidate_email,
        subject=f"🎉 Your referral for {job_title} at {company} was accepted!",
        html_body=html
    )
