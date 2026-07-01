import httpx
from config import config
from observability.logger import logger

class CopilotService:
    def __init__(self, http_client: httpx.AsyncClient):
        self.client = http_client
        self.copilot_url = config.COPILOT_URL
        
    async def send_message(self, text: str, conversation_id: str) -> str:
        """
        Forwards the user's message to Copilot Studio (via Power Automate or Direct Line URL)
        along with the conversation_id to maintain conversational context!
        """
        if not self.copilot_url:
            logger.error("COPILOT_URL is missing in environment variables.")
            return "Configuration Error: COPILOT_URL is not set in the environment variables."
            
        try:
            logger.info(f"Forwarding user message to Copilot Studio webhook...")
            logger.debug(f"Payload: conversationId={conversation_id}")
            
            response = await self.client.post(
                self.copilot_url,
                json={
                    "text": text,
                    "message": text,
                    "conversationId": conversation_id,
                    "conversation_id": conversation_id
                }
            )
            response.raise_for_status()
            
            logger.info("Successfully received response from Copilot Studio webhook.")
            
            # Safely parse the JSON response
            data = response.json()
            
            # DEBUG: Print the exact JSON returned from Copilot Studio to the terminal
            import json
            logger.info(f"RAW COPILOT JSON: {json.dumps(data, indent=2)}")
            
            # Try to find common response keys in the root
            if "response_message" in data and data["response_message"]:
                return data["response_message"]
            elif "response" in data and data["response"]:
                return data["response"]
            elif "text" in data and data["text"]:
                return data["text"]
            elif "answer" in data and data["answer"]:
                return data["answer"]
                
            # If root fields are empty, aggressively search the "activities" array for Adaptive Cards or message text
            # This is critical for capturing Microsoft's "Connection Consent" prompts!
            # Sometimes Copilot Studio wraps the response inside a "body" object
            payload = data.get("body", data)
            
            if "activities" in payload and isinstance(payload["activities"], list):
                for activity in reversed(payload["activities"]):
                    if activity.get("type") == "message":
                        # Check for raw text
                        if "text" in activity and activity["text"]:
                            return activity["text"]
                        
                        # Check for Adaptive Cards
                        if "attachments" in activity:
                            for attachment in activity["attachments"]:
                                if attachment.get("contentType") == "application/vnd.microsoft.card.adaptive":
                                    card_body = attachment.get("content", {}).get("body", [])
                                    card_text = []
                                    for item in card_body:
                                        if item.get("type") == "TextBlock" and "text" in item:
                                            card_text.append(item["text"])
                                    
                                    if card_text:
                                        # If it's a connection prompt, format it nicely
                                        return "Copilot Studio requires you to authorize the new connection:\n\n" + "\n".join(card_text)
            
            # If we still can't find anything, return a warning
            if "response_message" in data:
                return "Copilot Studio returned an empty response. Check your Power Automate flow to ensure the AI's output is being passed to the HTTP Response node."
                
            # If we can't find a known key, return the raw JSON so the user can debug their Copilot flow
            import json
            return f"Raw Copilot Output: {json.dumps(data, indent=2)}"
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error communicating with Copilot Studio: {str(e)}")
            return f"Error communicating with Copilot Studio: {str(e)}"
        except Exception as e:
            logger.exception("Unexpected error in CopilotService")
            return f"Unexpected error: {str(e)}"
