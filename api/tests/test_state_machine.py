from agents.state_machine import ConversationStateMachine, ConversationStep


def test_state_machine_initialization():
    """Test state machine initializes correctly"""
    sm = ConversationStateMachine()
    assert sm.current_step == ConversationStep.GREETING
    assert sm.collected_data == {}
    assert sm.conversation_history == []


def test_state_machine_advance():
    """Test state machine advances through states"""
    sm = ConversationStateMachine()
    
    # Advance from greeting
    sm.advance("Yes, I have time", {"confirmed": True})
    assert sm.current_step == ConversationStep.NAME_COLLECTION
    
    # Advance from name collection
    sm.advance("My name is John Doe", {"name": "John Doe"})
    assert sm.current_step == ConversationStep.DOB_COLLECTION
    assert sm.collected_data["name"] == "John Doe"


def test_state_machine_get_prompt():
    """Test getting current prompt"""
    sm = ConversationStateMachine()
    prompt = sm.get_current_prompt()
    assert "Hello" in prompt or "hello" in prompt
    assert len(prompt) > 0


def test_state_machine_is_completed():
    """Test completion check"""
    sm = ConversationStateMachine()
    assert not sm.is_completed()
    
    # Set to completed state
    sm.current_step = ConversationStep.COMPLETED
    assert sm.is_completed()


def test_state_machine_get_state():
    """Test getting state for persistence"""
    sm = ConversationStateMachine()
    sm.advance("Yes", {})
    
    state = sm.get_state()
    assert "current_step" in state
    assert "collected_data" in state
    assert "conversation_history" in state


def test_state_machine_restore_state():
    """Test restoring from saved state"""
    # Create initial state
    sm1 = ConversationStateMachine()
    sm1.advance("Yes", {"confirmed": True})
    sm1.advance("John Doe", {"name": "John Doe"})
    
    # Save state
    state = sm1.get_state()
    
    # Restore state
    sm2 = ConversationStateMachine(state)
    assert sm2.current_step == sm1.current_step
    assert sm2.collected_data == sm1.collected_data
