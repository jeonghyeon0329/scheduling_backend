import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string

def send_reset_email_async(to_email, reset_url, user_name):

    def _send():
        try:
            subject = "비밀번호 재설정 안내"
            from_email = "noreply@example.com"

            text_content = f"Reset your password here: {reset_url}"

            html_content = render_to_string(
                "reset_password.html",
                {"reset_url": reset_url, "user_name": user_name}
            )

            msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

        except Exception as e:
            # logger
            print("❌ Email send failed:", e)   

    threading.Thread(target=_send, daemon=True).start()
