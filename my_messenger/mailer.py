import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ============================================================
# ⚠️ ЗАПОЛНЕНО ТВОИМИ ДАННЫМИ
# ============================================================
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "ssssssqeeq@gmail.com"
SENDER_PASSWORD = "poyppjfbmioqfjhy"  # Пароль приложения (без пробелов)

def send_verification_code(to_email, code):
    """Отправляет красивое HTML-письмо с кодом"""
    subject = "Код подтверждения — Corvox Chat"
    
    html_body = f"""
    <html>
    <body style="margin:0; padding:0; background-color:#0c091d; font-family: Arial, sans-serif;">
      <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#0c091d; padding:40px 0;">
        <tr>
          <td align="center">
            <table width="420" cellpadding="0" cellspacing="0" style="background-color:#160f2d; border-radius:16px; padding:40px; border:1px solid #2a2440;">
              <tr>
                <td align="center" style="padding-bottom:16px;">
                  <div style="font-size:48px; color:#6246ff; font-weight:bold;">C</div>
                </td>
              </tr>
              <tr>
                <td align="center" style="padding-bottom:8px;">
                  <h1 style="color:#ffffff; font-size:22px; margin:0;">Добро пожаловать в Corvox Chat</h1>
                </td>
              </tr>
              <tr>
                <td align="center" style="padding-bottom:24px;">
                  <p style="color:#8b88a3; font-size:14px; margin:0;">Ваш код подтверждения:</p>
                </td>
              </tr>
              <tr>
                <td align="center">
                  <div style="background-color:#6246ff; color:#ffffff; font-size:32px; font-weight:bold; padding:20px 30px; border-radius:12px; letter-spacing:10px; display:inline-block;">
                    {code}
                  </div>
                </td>
              </tr>
              <tr>
                <td align="center" style="padding-top:32px;">
                  <p style="color:#8b88a3; font-size:12px; line-height:1.6; margin:0;">
                    Если вы не запрашивали этот код — просто проигнорируйте данное письмо.<br>
                    Никому не сообщайте свой код.
                  </p>
                </td>
              </tr>
            </table>
          </td>
        </tr>
      </table>
    </body>
    </html>
    """
    
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
        server.quit()
        print(f"[+] Письмо успешно отправлено на {to_email}")
        return True, "Код отправлен"
    except Exception as e:
        print(f"[!] Ошибка отправки письма: {e}")
        return False, str(e)