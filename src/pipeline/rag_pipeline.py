import chromadb
from src.models.llm_manager import get_embedding, generate_answer

class RAGPipeline:
    def __init__(self, collection_name: str = "rag_collection"):
        """ Khởi tạo bộ lưu trữ in-memory của ChromaDB """
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection(collection_name)

    def add_documents(self, chunks: list):
        """ Vector hóa các chunk văn bản và đẩy vào Vector Database """
        embeddings = get_embedding(chunks)
        self.collection.add(
            ids=[str(i) for i in range(len(chunks))],
            documents=chunks,
            embeddings=embeddings
        )

    def retrieve(self, query: str, k: int = 4) -> list:
        """ Tìm kiếm top-k đoạn văn bản có độ tương đồng cao nhất với câu hỏi """
        query_vector = get_embedding([query])
        res = self.collection.query(query_embeddings=query_vector, n_results=k)
        return res["documents"][0]