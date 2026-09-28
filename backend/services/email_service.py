import os
import resend

from backend.apps.config import settings


class EmailService:

    def send_lead(self, lead):

        # ------------------------------------------------------
        # Validate Resend configuration
        # ------------------------------------------------------

        resend_api_key = os.getenv("RESEND_API_KEY")

        if not resend_api_key:
            print(
                "RESEND_API_KEY not found. "
                "Skipping email."
            )
            return False

        if not settings.COMPANY_EMAIL:
            print(
                "COMPANY_EMAIL not found. "
                "Skipping email."
            )
            return False

        # ------------------------------------------------------
        # Configure Resend
        # ------------------------------------------------------

        resend.api_key = resend_api_key

        # ------------------------------------------------------
        # Build email
        # ------------------------------------------------------

        subject = (
            f"New Booking Enquiry - "
            f"{lead.name or 'Customer'}"
        )

        body = f"""
A new booking enquiry has been submitted.

---------------------------------------
CUSTOMER DETAILS
---------------------------------------

Name:
{lead.name}

Country:
{lead.country}

Language:
{lead.language}

---------------------------------------
CONTACT DETAILS
---------------------------------------

Phone:
{lead.phone}

Email:
{lead.email}

---------------------------------------
TRAVEL DETAILS
---------------------------------------

Destination:
{lead.destination}

Travel Date:
{lead.travel_date}

Travellers:
{lead.travellers}

Traveller Type:
{lead.traveller_type}

Children Travelling:
{lead.children_travelling}

Budget:
{lead.budget}

Visa Required:
{lead.visa_required}

Special Requests:
{lead.special_requests}

---------------------------------------
BOOKING STATUS
---------------------------------------

Status:
{lead.status}
"""

        # ------------------------------------------------------
        # Send using Resend HTTPS API
        # ------------------------------------------------------

        try:

            print(
                "EMAIL: Sending booking email using Resend..."
            )

            response = resend.Emails.send({
                "from": "Stanley Tours AI <bookings@stanleytour.com>",
                "to": [settings.COMPANY_EMAIL],
                "subject": subject,
                "text": body,
            })

            print(
                "EMAIL SENT SUCCESSFULLY."
            )

            print(
                "RESEND RESPONSE:",
                response
            )

            return True

        except Exception as exc:

            print(
                "EMAIL ERROR:",
                type(exc).__name__,
                repr(exc)
            )

            return False


email_service = EmailService()