from typing import Dict, Any, List, Optional
from enum import Enum
import json


class ConversationStep(str, Enum):
    """States in the patient intake conversation flow"""
    GREETING = "greeting"
    NAME_COLLECTION = "name_collection"
    DOB_COLLECTION = "dob_collection"
    REASON_FOR_VISIT = "reason_for_visit"
    SYMPTOMS = "symptoms"
    MEDICAL_HISTORY = "medical_history"
    MEDICATIONS = "medications"
    ALLERGIES = "allergies"
    INSURANCE = "insurance"
    CONFIRMATION = "confirmation"
    CLOSING = "closing"
    COMPLETED = "completed"


class ConversationStateMachine:
    """
    Manages the conversation flow for patient intake
    """
    
    # Define the conversation flow
    FLOW = {
        ConversationStep.GREETING: ConversationStep.NAME_COLLECTION,
        ConversationStep.NAME_COLLECTION: ConversationStep.DOB_COLLECTION,
        ConversationStep.DOB_COLLECTION: ConversationStep.REASON_FOR_VISIT,
        ConversationStep.REASON_FOR_VISIT: ConversationStep.SYMPTOMS,
        ConversationStep.SYMPTOMS: ConversationStep.MEDICAL_HISTORY,
        ConversationStep.MEDICAL_HISTORY: ConversationStep.MEDICATIONS,
        ConversationStep.MEDICATIONS: ConversationStep.ALLERGIES,
        ConversationStep.ALLERGIES: ConversationStep.INSURANCE,
        ConversationStep.INSURANCE: ConversationStep.CONFIRMATION,
        ConversationStep.CONFIRMATION: ConversationStep.CLOSING,
        ConversationStep.CLOSING: ConversationStep.COMPLETED,
    }
    
    # Prompts for each conversation step
    PROMPTS = {
        ConversationStep.GREETING: (
            "Hello! I'm calling from the medical clinic. "
            "I'm here to help you with your appointment intake. "
            "This call will help us prepare for your visit. May I have a moment of your time?"
        ),
        ConversationStep.NAME_COLLECTION: (
            "Great! To get started, could you please tell me your full name?"
        ),
        ConversationStep.DOB_COLLECTION: (
            "Thank you. And could you please provide your date of birth?"
        ),
        ConversationStep.REASON_FOR_VISIT: (
            "Thank you for that information. What is the main reason for your visit today?"
        ),
        ConversationStep.SYMPTOMS: (
            "I understand. Can you describe any symptoms you're experiencing? "
            "Please take your time and share as much detail as you're comfortable with."
        ),
        ConversationStep.MEDICAL_HISTORY: (
            "Thank you for sharing. Do you have any existing medical conditions "
            "or significant medical history we should know about?"
        ),
        ConversationStep.MEDICATIONS: (
            "Got it. Are you currently taking any medications, including over-the-counter drugs "
            "or supplements?"
        ),
        ConversationStep.ALLERGIES: (
            "Thank you. Do you have any known allergies, particularly to medications?"
        ),
        ConversationStep.INSURANCE: (
            "Almost done! Do you have health insurance? If so, could you provide "
            "your insurance provider and member ID?"
        ),
        ConversationStep.CONFIRMATION: (
            "Let me confirm the information I've collected. "
            "{summary} Is this information correct?"
        ),
        ConversationStep.CLOSING: (
            "Perfect! We have all the information we need for your appointment. "
            "Thank you so much for your time. Is there anything else you'd like to share "
            "or any questions you have?"
        ),
    }
    
    def __init__(self, initial_state: Optional[Dict[str, Any]] = None):
        """
        Initialize the state machine
        
        Args:
            initial_state: Existing conversation state to resume from
        """
        if initial_state:
            self.current_step = ConversationStep(initial_state.get("current_step", ConversationStep.GREETING))
            self.collected_data = initial_state.get("collected_data", {})
            self.conversation_history = initial_state.get("conversation_history", [])
        else:
            self.current_step = ConversationStep.GREETING
            self.collected_data = {}
            self.conversation_history = []
    
    def get_current_prompt(self) -> str:
        """Get the prompt for the current conversation step"""
        prompt = self.PROMPTS.get(self.current_step, "")
        
        # Special handling for confirmation step
        if self.current_step == ConversationStep.CONFIRMATION:
            summary = self._generate_summary()
            prompt = prompt.format(summary=summary)
        
        return prompt
    
    def advance(self, user_response: str, extracted_data: Optional[Dict[str, Any]] = None):
        """
        Advance to the next step in the conversation
        
        Args:
            user_response: The user's response to the current prompt
            extracted_data: Data extracted from the user's response
        """
        # Store the interaction
        self.conversation_history.append({
            "step": self.current_step.value,
            "prompt": self.get_current_prompt(),
            "response": user_response,
            "extracted_data": extracted_data
        })
        
        # Update collected data
        if extracted_data:
            self.collected_data.update(extracted_data)
        
        # Move to next step
        next_step = self.FLOW.get(self.current_step)
        if next_step:
            self.current_step = next_step
    
    def is_completed(self) -> bool:
        """Check if the conversation is completed"""
        return self.current_step == ConversationStep.COMPLETED
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state for persistence"""
        return {
            "current_step": self.current_step.value,
            "collected_data": self.collected_data,
            "conversation_history": self.conversation_history
        }
    
    def _generate_summary(self) -> str:
        """Generate a summary of collected data for confirmation"""
        data = self.collected_data
        summary_parts = []
        
        if "name" in data:
            summary_parts.append(f"Name: {data['name']}")
        if "dob" in data:
            summary_parts.append(f"Date of birth: {data['dob']}")
        if "reason" in data:
            summary_parts.append(f"Reason for visit: {data['reason']}")
        if "symptoms" in data:
            summary_parts.append(f"Symptoms: {data['symptoms']}")
        if "medical_history" in data:
            summary_parts.append(f"Medical history: {data['medical_history']}")
        if "medications" in data:
            summary_parts.append(f"Current medications: {data['medications']}")
        if "allergies" in data:
            summary_parts.append(f"Allergies: {data['allergies']}")
        if "insurance" in data:
            summary_parts.append(f"Insurance: {data['insurance']}")
        
        return ". ".join(summary_parts) + "."
    
    def should_clarify(self, user_response: str) -> bool:
        """
        Determine if we need to ask for clarification
        
        Args:
            user_response: The user's response
            
        Returns:
            True if clarification is needed
        """
        # Simple heuristic: if response is too short or ambiguous
        unclear_responses = ["huh", "what", "i don't know", "not sure", "maybe"]
        response_lower = user_response.lower().strip()
        
        return (
            len(response_lower) < 3 or
            any(phrase in response_lower for phrase in unclear_responses)
        )
