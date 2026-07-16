import re

class QuizManager:
    """
    Manages the lifecycle and state transitions of the interactive quiz feature.
    This class handles question parsing, state tracking, and score management.
    """
    def __init__(self):
        # Initialize the state machine to track user progress and quiz metadata
        self.state = {
            "step": 0,          # Current state: 0 (IDLE), 1 (TOPIC), 2 (QUANTITY), 3 (ACTIVE)
            "topic": None,      # Subject matter of the quiz
            "num": 0,           # Total number of questions requested
            "current_index": 0, # Index of the question currently being presented
            "questions": [],    # List of structured question dictionaries
            "score": 0          # Count of correct user responses
        }

    def parse_questions(self, text):
        """
        Parses raw unstructured text from the LLM into a structured list of dictionaries.
        
        Args:
            text (str): The raw string output from the inference engine.
            
        Returns:
            list: A list of objects containing the question, options, and the correct answer.
        """
        # Regex pattern to capture the question, four options (a-d), and the answer key
        pattern = r"(\d+\..+?)\s+(a\).+?)\s+(b\).+?)\s+(c\).+?)\s+(d\).+?)\s+Answer:\s*([a-d])"
        matches = re.findall(pattern, text, re.DOTALL | re.IGNORECASE)
        
        parsed_list = []
        for m in matches:
            # Map regex captures to a structured data format for easy front-end rendering
            parsed_list.append({
                "question": m[0].strip(),
                "options": f"{m[1].strip()}\n{m[2].strip()}\n{m[3].strip()}\n{m[4].strip()}",
                "answer": m[5].lower().strip()
            })
        return parsed_list

    def reset(self):
        """
        Resets the internal state to default values upon quiz completion or termination.
        Ensures a clean state for subsequent quiz sessions.
        """
        self.state = {
            "step": 0, 
            "topic": None, 
            "num": 0, 
            "current_index": 0, 
            "questions": [], 
            "score": 0
        }

# Instantiate the QuizManager as a global singleton for consistent access across routes
quiz_bot = QuizManager()