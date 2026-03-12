import os
import hashlib
import chromadb
from chromadb.utils import embedding_functions
from tree_sitter_languages import get_parser, get_language

class CodeIndexer:
    def __init__(self, db_path="./chroma_db"):
        self.client = chromadb.PersistentClient(path=db_path)
        # Using a lightweight default embedding function for now
        # In production, we would use Gemini Flash for embeddings
        self.ef = embedding_functions.DefaultEmbeddingFunction()
        self.collection = self.client.get_or_create_collection(
            name="vouch_codebase",
            embedding_function=self.ef
        )
        self.index_metadata_collection = self.client.get_or_create_collection(
            name="vouch_metadata"
        )

    def _calculate_file_hash(self, content):
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def index_repository(self, repo_path):
        """Walks through the repository and indexes files."""
        indexed_files = []
        for root, _, files in os.walk(repo_path):
            for file in files:
                if file.endswith(('.py', '.js', '.jsx', '.ts', '.tsx')):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, repo_path)
                    
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                    
                    file_hash = self._calculate_file_hash(content)
                    
                    # Check if file has changed
                    existing_meta = self.index_metadata_collection.get(ids=[rel_path])
                    if existing_meta['ids'] and existing_meta['metadatas'][0]['hash'] == file_hash:
                        continue
                    
                    # Index symbols and update metadata
                    self._index_file_symbols(rel_path, content)
                    self.index_metadata_collection.upsert(
                        ids=[rel_path],
                        metadatas=[{"hash": file_hash, "path": rel_path}]
                    )
                    indexed_files.append(rel_path)
        return indexed_files

    def _index_file_symbols(self, file_path, content):
        """Parses a file with tree-sitter and indexes function/class definitions."""
        ext = os.path.splitext(file_path)[1]
        lang_name = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'tsx'
        }.get(ext)
        
        if not lang_name:
            return

        try:
            parser = get_parser(lang_name)
            tree = parser.parse(bytes(content, "utf8"))
            
            # Simple queries for definitions
            query_str = ""
            if lang_name == 'python':
                query_str = """
                (function_definition
                    name: (identifier) @name) @def
                (class_definition
                    name: (identifier) @name) @def
                """
            elif lang_name in ['javascript', 'typescript', 'tsx']:
                query_str = """
                (function_declaration
                    name: (identifier) @name) @def
                (method_definition
                    name: (property_identifier) @name) @def
                (class_declaration
                    name: (identifier) @name) @def
                (variable_declarator
                    name: (identifier) @name
                    value: (arrow_function)) @def
                """

            if not query_str:
                return

            language = get_language(lang_name)
            query = language.query(query_str)
            captures = query.captures(tree.root_node)
            
            # Group by @def and @name
            definitions = []
            for node, tag in captures:
                if tag == 'def':
                    start_byte = node.start_byte
                    end_byte = node.end_byte
                    code_snippet = content[start_byte:end_byte]
                    
                    # Find the corresponding name (usually the next capture or part of this node)
                    # For simplicity, we'll just store the snippet and the whole thing
                    definitions.append({
                        "id": f"{file_path}:{node.start_point[0]}",
                        "content": code_snippet,
                        "metadata": {
                            "file": file_path,
                            "line": node.start_point[0],
                            "type": node.type
                        }
                    })

            if definitions:
                # Clear old entries for this file
                # ChromaDB filtering by file metadata
                self.collection.delete(where={"file": file_path})
                
                self.collection.add(
                    ids=[d["id"] for d in definitions],
                    documents=[d["content"] for d in definitions],
                    metadatas=[d["metadata"] for d in definitions]
                )

        except Exception as e:
            print(f"Error indexing {file_path}: {e}")

    def query_context(self, code_snippet, n_results=3):
        """Finds relevant symbol definitions for a given piece of code."""
        results = self.collection.query(
            query_texts=[code_snippet],
            n_results=n_results
        )
        return results
