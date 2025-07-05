import json
from haystack import Pipeline, Document
from haystack.document_stores.in_memory import InMemoryDocumentStore
from haystack.components.embedders import SentenceTransformersDocumentEmbedder, SentenceTransformersTextEmbedder
from haystack.components.retrievers.in_memory import InMemoryEmbeddingRetriever
from haystack.components.builders import ChatPromptBuilder
from haystack.components.generators.chat import OpenAIChatGenerator
from haystack.components.writers import DocumentWriter
from haystack.document_stores.types import DuplicatePolicy
from haystack.utils.hf import Secret
from haystack.dataclasses import ChatMessage

class EDAChatAgent:
    def __init__(self, api_key):
        self.document_store = InMemoryDocumentStore()
        self.document_embedder = SentenceTransformersDocumentEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
        self.document_writer = DocumentWriter(document_store=self.document_store, policy=DuplicatePolicy.SKIP)
        self.indexing = Pipeline()
        self.indexing.add_component(instance=self.document_embedder, name="document_embedder")
        self.indexing.add_component(instance=self.document_writer, name="document_writer")
        self.indexing.connect("document_embedder.documents", "document_writer.documents")
        self.text_embedder = SentenceTransformersTextEmbedder(model="sentence-transformers/all-MiniLM-L6-v2")
        self.retriever = InMemoryEmbeddingRetriever(self.document_store, top_k=5)
        self.generator = OpenAIChatGenerator(
            model="gpt-4o-mini",
            api_key=Secret.from_token(api_key)
        )
        
        self.prompt_template = [
            ChatMessage.from_user("""
                Rispondi usando il contesto EDA:
                
                {% for doc in documents %}
                {{ doc.content }}
                {% endfor %}
                
                Domanda: {{query}}
                
                Risposta:
            """)
        ]

        # Costruzione del prompt e della risposta
        #self.prompt_builder = ChatPromptBuilder(template=self.prompt_template)
        self.prompt_builder = ChatPromptBuilder(
            template=self.prompt_template,
            required_variables=["documents", "query"],
            variables=["documents", "query"]
        )

        self.pipeline = Pipeline()
        self.pipeline.add_component("query_embedder", self.text_embedder)
        self.pipeline.add_component("retriever", self.retriever)
        self.pipeline.add_component("prompt_builder", self.prompt_builder)
        self.pipeline.add_component("generator", self.generator)
        self.pipeline.connect("query_embedder", "retriever.query_embedding")
        self.pipeline.connect("retriever", "prompt_builder.documents")
        self.pipeline.connect("prompt_builder.prompt", "generator.messages")

    def index_eda(self, eda_json, upload_id):
        eda_text = json.dumps(eda_json, indent=2)
        doc = Document(content=eda_text, meta={"upload_id": upload_id})
        self.indexing.run({"document_embedder": {"documents": [doc]}})

    def answer(self, question):
        result = self.pipeline.run({
            "query_embedder": {"text": question},
            "prompt_builder": {"query": question}
        })
        return result["generator"]["replies"][0]