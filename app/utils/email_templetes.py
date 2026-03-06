import os
from datetime import datetime
from dotenv import load_dotenv
import pytz

# Load environment variables to get FRONTEND_URL
load_dotenv()

def ist_timezone(utc_time_str):
    if isinstance(utc_time_str, str):
        utc_time = datetime.fromisoformat(utc_time_str)
    elif isinstance(utc_time_str, datetime):
        utc_time = utc_time_str
    else:
        raise TypeError("Unsupported type for utc_time_input")
    ist = pytz.timezone("Asia/Kolkata")
    ist_time = utc_time.astimezone(ist)

    # Separate date and time
    date_str = ist_time.date().isoformat()
    time_str = ist_time.time().strftime("%H:%M")    
    return date_str, time_str

def booking_confirmation_template(user_name, doctor_name, booking_date, booking_id):
    """
    Generates email content for a new booking confirmation.
    """
    response=ist_timezone(booking_date)
    date,time=response[0],response[1]
    subject = f"Booking Confirmed With {doctor_name}"
    
    body = f"""
Hi {user_name},

Your appointment has been successfully booked.

Doctor: {doctor_name}  
Date: {date}
Time: {time}

Booking ID: {booking_id}
You can view your booking details and manage your appointments by logging into your account.    

Thanks,
The Team
"""
    return {"subject": subject, "body": body.strip()}


def appointment_reminder_template(user_name, doctor_name, appointment_time,booking_id=111):
    """
    Generates email content for an appointment reminder.

    """
    response=ist_timezone(appointment_time)
    date,time=response[0],response[1]
    subject = f"Reminder: Appointment With {doctor_name}"
    
    body = f"""
Hi {user_name},

This is a gentle reminder about your upcoming appointment.

Doctor: {doctor_name}
Date: {date}
Time: {time}

Booking ID: {booking_id}
You can view your booking details and manage your appointments by logging into your account.    


Thanks,
The Team
"""
    
    return {"subject": subject, "body": body.strip()}


def password_reset_template(user_name, reset_link):
    """
    Generates email content for password reset.
    """
    subject = "Password Reset Request"
    
    body = f"""
Hi {user_name},
We received a request to reset your password. Click the link below to set a new password:
{reset_link}
If you did not request a password reset, please ignore this email.
Thanks,
The Team
"""
    return {"subject": subject, "body": body.strip()}


def otp_verification_template( otp_code):
    """
    Generates email content for OTP verification.
    """
    subject = "OTP To Login skinSage"
    
    body = f"""
Hi,
your OTP code is: {otp_code}
This code is valid for the next 10 minutes. Please do not share this code with anyone

Thanks,
The Team
"""
    return {"subject": subject, "body": body.strip()}


def provider_welcome_template(user_name, reset_link):
    """
    Generates email content for a new provider welcome email.
    """
    subject = "Welcome to skinSage! Please set your password"
    
    body = f"""
Hi {user_name},

An account has been created for you. Please click the link below to set your password and log in:
{reset_link}

If you have any questions, please contact the administration.

Thanks,
The Team
"""
    return {"subject": subject, "body": body.strip()}
