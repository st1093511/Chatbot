from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from sqlalchemy import create_engine, text
import os

class TextToSQL:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        # Assuming SQLite for simplicity
        self.engine = create_engine("sqlite:///db/chatbot.db")
        
    def process(self, query: str) -> str:
        prompt = PromptTemplate.from_template("""
        Convert the following natural language query to SQL:
        {query}
        
        Database schema: [Describe your schema here]
        
        Return only the SQL query.
        """)
        chain = prompt | self.llm
        sql_query = chain.invoke({"query": query}).content.strip()
        
        # Execute the query
        with self.engine.connect() as conn:
            result = conn.execute(text(sql_query))
            rows = result.fetchall()
        
        return str(rows)