"""
Mock Google Generative AI module for development when the real package isn't available
"""

class MockGenerativeModel:
    def __init__(self, model_name):
        self.model_name = model_name
    
    def generate_content(self, prompt):
        return MockResponse("Mock AI response - Google Generative AI not configured")

class MockResponse:
    def __init__(self, text):
        self.text = text

def configure(api_key=None):
    """Mock configure function"""
    pass

def GenerativeModel(model_name):
    """Mock GenerativeModel class"""
    return MockGenerativeModel(model_name)