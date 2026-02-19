from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_carenova_email(subject, to_email, context, template_name):
    """
    Base function to send HTML emails.
    """
    from_email = settings.DEFAULT_FROM_EMAIL
    
    # Render the HTML version of the email
    html_content = render_to_string(f'emails/{template_name}.html', context)
    # Create a plain text version for email clients that don't support HTML
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {str(e)}")
        return False