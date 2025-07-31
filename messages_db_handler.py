from pymongo import MongoClient
from datetime import datetime

# Setup MongoDB connection
client = MongoClient("mongodb://localhost:27017/")
db = client["facebook_messages_db"]
messages_col = db["messages"]
conversations_col = db["conversations"]


def save_incoming_message_to_db(webhook_data: dict):
    try:
        entry = webhook_data.get("entry", [])[0]
        messaging_event = entry.get("messaging", [])[0]

        sender_id = messaging_event.get("sender", {}).get("id")
        recipient_id = messaging_event.get("recipient", {}).get("id")
        message = messaging_event.get("message", {})
        message_text = message.get("text", "")
        message_id = message.get("mid", "")
        timestamp = datetime.utcfromtimestamp(messaging_event.get("timestamp") / 1000.0)

        conversation_id = f"{recipient_id}_{sender_id}"

        message_doc = {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "sender_id": sender_id,
            "receiver_id": recipient_id,
            "direction": "incoming",
            "message_text": message_text,
            "message_type": "text",
            "timestamp": timestamp.isoformat(),
            "raw_payload": messaging_event,
            "tags": []
        }

        messages_col.insert_one(message_doc)
        print("[✓] Message saved to MongoDB.")

    except Exception as e:
        print(f"[✗] Failed to save message: {e}")



def save_outgoing_message_to_db(response_data: dict, sender_id: str, recipient_id: str, message_text: str):
    """
    Save an outgoing message (sent via FB API) to MongoDB.

    :param response_data: The response returned from Facebook Send API
    :param sender_id: The page ID (you sent the message from)
    :param recipient_id: The user ID (you sent the message to)
    :param message_text: The actual message text sent
    """
    try:
        message_id = response_data.get("message_id")
        conversation_id = f"{sender_id}_{recipient_id}"
        timestamp = datetime.utcnow()

        message_doc = {
            "conversation_id": conversation_id,
            "message_id": message_id,
            "sender_id": sender_id,
            "receiver_id": recipient_id,
            "direction": "outgoing",
            "message_text": message_text,
            "message_type": "text",
            "timestamp": timestamp.isoformat(),
            "raw_payload": response_data,
            "tags": []
        }

        messages_col.insert_one(message_doc)
        print("[✓] Outgoing message saved to MongoDB.")

    except Exception as e:
        print(f"[✗] Failed to save outgoing message: {e}")


def upsert_conversation_session(sender_id: str, recipient_id: str, timestamp: datetime, direction: str):
    """
    Ensures a conversation session is created or updated.
    
    :param sender_id: The user or page sending the message
    :param recipient_id: The user or page receiving the message
    :param timestamp: Datetime of the message
    :param direction: "incoming" or "outgoing"
    """
    try:
        if direction == "incoming":
            user_id = sender_id
            page_id = recipient_id
        else:
            user_id = recipient_id
            page_id = sender_id

        conversation_id = f"{page_id}_{user_id}"

        conversations_col.update_one(
            {"conversation_id": conversation_id},
            {
                "$set": {
                    "user_id": user_id,
                    "page_id": page_id,
                    "status": "active",
                    "last_updated": timestamp.isoformat()
                },
            "$setOnInsert": {
                "context_summary": "",
                "tags": [],
                "has_complaint": False,
                "last_complaint_id": None
            }
            },
            upsert=True
        )

        print(f"[✓] Conversation '{conversation_id}' upserted.")

    except Exception as e:
        print(f"[✗] Failed to upsert conversation: {e}")


def build_llm_context(conversation_id: str, limit: int = 10) -> list:
    """
    Builds a list of recent messages formatted for LLM prompt context.
    
    :param conversation_id: ID of the conversation (e.g., PAGEID_USERID)
    :param limit: Number of recent messages to include (default 10)
    :return: List of dicts formatted as [{"role": ..., "content": ...}]
    """
    try:
        # Fetch last N messages sorted by time
        messages = list(
            messages_col.find({"conversation_id": conversation_id})
            .sort("timestamp", -1)
            .limit(limit)
        )
        messages.reverse()  # reverse to chronological order

        formatted_context = []
        for msg in messages:
            role = "user" if msg["direction"] == "incoming" else "assistant"
            content = msg.get("message_text", "")
            if content.strip():  # skip empty messages
                formatted_context.append({
                    "role": role,
                    "content": content
                })

        return formatted_context

    except Exception as e:
        print(f"[✗] Failed to build LLM context: {e}")
        return []
    
complaints_col = db["complaints"]

def create_complaint(conversation_id: str, user_id: str, message_ids: list, full_text: str, summary: str, duplicate_of=None):
    complaint_doc = {
        "conversation_id": conversation_id,
        "user_id": user_id,
        "full_text": full_text,
        "summary": summary,
        "status": "pending",
        "duplicate_of": duplicate_of,
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "spam_flag": False,
        "source_message_ids": message_ids,
        "escalation_channel": "email",
        "escalated_to": None,
        "internal_notes": ""
    }

    result = complaints_col.insert_one(complaint_doc)
    return result.inserted_id
