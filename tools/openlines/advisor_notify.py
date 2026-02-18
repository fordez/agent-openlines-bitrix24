"""
Tool to send direct system notifications to advisors in Bitrix24.
Uses: im.notify.system.add
"""
from app.auth import call_bitrix_method
import sys

async def advisor_notify(user_id: int, message: str, access_token: str = None, domain: str = None) -> str:
    """
    Sends a direct system notification to a specific Bitrix24 user (advisor).
    
    Args:
        user_id: ID of the user to notify.
        message: The notification text.
    """
    if not user_id or not message:
        return "Error: user_id and message are required."

    sys.stderr.write(f"  🔔 Tool advisor_notify: User {user_id}\n")

    params = {
        "USER_ID": user_id,
        "MESSAGE": message,
        "NOTIFY_TYPE": 2,  # 2 = System notification
    }

    try:
        result = await call_bitrix_method("im.notify.system.add", params, access_token=access_token, domain=domain)
        if result.get("result"):
            return f"Notification sent to user {user_id}."
        else:
            error = result.get("error_description", result)
            return f"Error sending notification: {error}"
    except Exception as e:
        return f"Error in advisor_notify: {e}"
