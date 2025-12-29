import os
import uuid



def base_template_builder(company_id: str | uuid.UUID, client_id: str | uuid.UUID, tracking_id: str | uuid.UUID) -> str:
    host = os.getenv("HOST")

    review_url = (
        f"{host}/invitations/review/"
        f"{company_id}/{client_id}/{tracking_id}"
    )

    return f"""
    <!DOCTYPE html>
    <html lang="pl">
    <head>
        <meta charset="UTF-8">
    </head>
    <body style="margin:0; padding:0; background-color:#f4f6f8; font-family:Arial, Helvetica, sans-serif;">

    <table width="100%" cellpadding="0" cellspacing="0" style="padding:20px;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff; border-radius:12px; overflow:hidden;">

                    <tr>
                        <td style="background:linear-gradient(90deg,#6366f1,#8b5cf6); padding:30px; color:#ffffff;">
                            <h1 style="margin:0; font-size:26px;">
                                Dziękujemy za skorzystanie z naszych usług!
                            </h1>
                        </td>
                    </tr>

                    <tr>
                        <td style="padding:30px; color:#111827;">
                            <p style="font-size:16px;">
                                Dzień dobry <strong>{{{{imię}}}}</strong>,
                            </p>

                            <table cellpadding="0" cellspacing="0" style="margin:30px 0;">
                                <tr>
                                    <td align="center">
                                        <a href="{review_url}"
                                           style="display:inline-block; padding:14px 28px;
                                                  background-color:#6366f1; color:#ffffff;
                                                  text-decoration:none; font-size:16px;
                                                  font-weight:bold; border-radius:8px;">
                                            ⭐ Zostaw opinię
                                        </a>
                                    </td>
                                </tr>
                            </table>

                            <p style="font-size:14px; color:#6b7280;">
                                Dziękujemy za Twój czas i zaufanie.
                            </p>

                            <p>
                                Pozdrawiamy,<br>
                                <strong>{{{{nazwa_firmy}}}}</strong>
                            </p>
                        </td>
                    </tr>

                    <tr>
                        <td style="background:#f9fafb; padding:20px; text-align:center;
                                   font-size:12px; color:#9ca3af;">
                            © 2026 {{{{nazwa_firmy}}}}
                        </td>
                    </tr>

                </table>
            </td>
        </tr>
    </table>

    </body>
    </html>
    """
