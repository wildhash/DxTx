from openai import AsyncOpenAI
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / 'api'))
from app.config import settings
from typing import Dict, Any, Optional, List
import json
import logging

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)


class EmpatheticAgent:
    """
    LLM-powered empathetic dialogue agent for patient intake
    """
    
    SYSTEM_PROMPT = """You are a compassionate and empathetic AI medical intake assistant. Your role is to:

1. Make patients feel comfortable and heard
2. Gather necessary medical information for their appointment
3. Show empathy and understanding for their concerns
4. Ask clarifying questions when needed
5. Maintain HIPAA compliance by being professional and discrete

Guidelines:
- Use a warm, friendly tone
- Acknowledge patient concerns and emotions
- Ask one question at a time
- Rephrase or clarify if the patient seems confused
- Never provide medical advice or diagnosis
- Be patient and give them time to think
- Use simple, clear language
- Show empathy phrases like "I understand", "That must be difficult", "Thank you for sharing"

You are currently helping with patient intake before their appointment."""
    
    def __init__(self):
        self.model = settings.OPENAI_MODEL
    
    async def generate_response(
        self,
        conversation_history: List[Dict[str, str]],
        current_prompt: str,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate an empathetic response using LLM
        
        Args:
            conversation_history: Previous conversation turns
            current_prompt: The scripted prompt for this conversation step
            user_input: What the patient just said
            context: Additional context about the conversation
            
        Returns:
            AI-generated empathetic response
        """
        try:
            # Build conversation context
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ]
            
            # Add conversation history
            for turn in conversation_history[-5:]:  # Last 5 turns for context
                if turn.get("prompt"):
                    messages.append({"role": "assistant", "content": turn["prompt"]})
                if turn.get("response"):
                    messages.append({"role": "user", "content": turn["response"]})
            
            # Add current interaction
            messages.append({"role": "assistant", "content": current_prompt})
            messages.append({"role": "user", "content": user_input})
            
            # Add instruction for response
            instruction = (
                "Based on the patient's response, provide an empathetic acknowledgment "
                "and then guide them appropriately. If their answer is complete and clear, "
                "acknowledge it warmly. If it's unclear or incomplete, ask a gentle clarifying question."
            )
            messages.append({"role": "system", "content": instruction})
            
            # Generate response
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=200
            )
            
            ai_response = response.choices[0].message.content.strip()
            logger.info(f"Generated empathetic response: {ai_response[:100]}...")
            
            return ai_response
        
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            # Fallback to acknowledging response
            return "Thank you for sharing that with me."
    
    async def extract_information(
        self,
        user_input: str,
        expected_field: str
    ) -> Optional[Dict[str, Any]]:
        """
        Extract structured information from user input
        
        Args:
            user_input: What the patient said
            expected_field: What information we're trying to extract (name, dob, symptoms, etc.)
            
        Returns:
            Extracted structured data
        """
        try:
            extraction_prompt = f"""Extract the {expected_field} from the following patient response.
Return ONLY a JSON object with the extracted information.

Patient response: "{user_input}"

Expected format for {expected_field}:
"""
            
            # Field-specific extraction instructions
            if expected_field == "name":
                extraction_prompt += '{"name": "Full Name"}'
            elif expected_field == "dob":
                extraction_prompt += '{"dob": "MM/DD/YYYY or described date"}'
            elif expected_field == "reason":
                extraction_prompt += '{"reason": "Brief description of visit reason"}'
            elif expected_field == "symptoms":
                extraction_prompt += '{"symptoms": "Description of symptoms"}'
            elif expected_field == "medical_history":
                extraction_prompt += '{"medical_history": "Existing conditions or N/A"}'
            elif expected_field == "medications":
                extraction_prompt += '{"medications": "List of medications or N/A"}'
            elif expected_field == "allergies":
                extraction_prompt += '{"allergies": "List of allergies or N/A"}'
            elif expected_field == "insurance":
                extraction_prompt += '{"insurance": "Insurance provider and ID or N/A"}'
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data extraction assistant. Extract only the requested information and return valid JSON."},
                    {"role": "user", "content": extraction_prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )
            
            extracted_text = response.choices[0].message.content.strip()
            
            # Try to parse JSON
            # Remove markdown code blocks if present
            if extracted_text.startswith("```"):
                extracted_text = extracted_text.split("```")[1]
                if extracted_text.startswith("json"):
                    extracted_text = extracted_text[4:]
                extracted_text = extracted_text.strip()
            
            extracted_data = json.loads(extracted_text)
            logger.info(f"Extracted {expected_field}: {extracted_data}")
            
            return extracted_data
        
        except Exception as e:
            logger.error(f"Error extracting information: {e}")
            return None
    
    async def detect_sentiment(self, user_input: str) -> str:
        """
        Detect patient sentiment (anxious, calm, frustrated, etc.)
        
        Args:
            user_input: What the patient said
            
        Returns:
            Detected sentiment
        """
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a sentiment analysis assistant. Analyze the emotional tone of patient responses."},
                    {"role": "user", "content": f"What is the emotional sentiment of this patient response? Reply with ONE WORD only (calm, anxious, frustrated, scared, happy, neutral, etc.)\n\nPatient: {user_input}"}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            sentiment = response.choices[0].message.content.strip().lower()
            logger.info(f"Detected sentiment: {sentiment}")
            
            return sentiment
        
        except Exception as e:
            logger.error(f"Error detecting sentiment: {e}")
            return "neutral"
    
    async def generate_summary(
        self,
        conversation_history: List[Dict[str, str]],
        collected_data: Dict[str, Any]
    ) -> str:
        """
        Generate an AI summary of the conversation
        
        Args:
            conversation_history: Full conversation history
            collected_data: Structured data collected
            
        Returns:
            AI-generated summary
        """
        try:
            conversation_text = "\n".join([
                f"Agent: {turn.get('prompt', '')}\nPatient: {turn.get('response', '')}"
                for turn in conversation_history
            ])
            
            prompt = f"""Summarize this patient intake conversation. Include:
1. Patient information collected
2. Chief complaint and symptoms
3. Relevant medical history
4. Any concerns or questions raised
5. Overall patient sentiment/emotional state

Conversation:
{conversation_text}

Collected data:
{json.dumps(collected_data, indent=2)}

Provide a concise clinical summary suitable for medical records:"""
            
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a medical documentation assistant. Create concise, professional clinical summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"Generated summary")
            
            return summary
        
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Summary generation failed."


# Singleton instance
empathetic_agent = EmpatheticAgent()
