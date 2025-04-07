class TextLoader:

    def __init__(self):
        pass
    
    def load(self, file_content: bytes):
        """Load the text content from the file."""
        if isinstance(file_content, bytes):
            self.content = file_content.decode('utf-8')
        else:
            raise ValueError("File content must be in bytes.")
        
        return self.content