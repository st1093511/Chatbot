from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

class CRUDHandler:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        
    def process(self, message: str) -> str:
        prompt = PromptTemplate.from_template("""
        Analyze the following message and determine if it's a CRUD operation (Create, Read, Update, Delete) on data.
        If it is, perform the operation and return the result.
        Otherwise, return an appropriate response.
        
        Message: {message}
        """)
        chain = prompt | self.llm
        response = chain.invoke({"message": message})
        return response.content.strip()