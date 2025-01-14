class BaseService:
    """Base class for all system services"""
    
    def __init__(self, name: str):
        self.name = name
        self.enabled = True
        
    async def initialize(self) -> bool:
        """Initialize the service"""
        return True
        
    async def cleanup(self):
        """Clean up service resources"""
        self.enabled = False