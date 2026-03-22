import chromadb
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA

class RAGPipeline:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini")
        self.embeddings = OpenAIEmbeddings()
        self.client = chromadb.PersistentClient(path="./db")
        
    def process(self, query: str) -> str:
        vectorstore = Chroma(
            client=self.client,
            collection_name="documents",
            embedding_function=self.embeddings
        )
        retriever = vectorstore.as_retriever()
        qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever
        )
        result = qa_chain.invoke({"query": query})
        return result["result"]