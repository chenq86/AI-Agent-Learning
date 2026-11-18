from langchain_chroma import Chroma
from utils.config_handler import chroma_conf
from model.factory import embed_model
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os
from utils.path_tool import get_abs_path
from utils.file_handler import pdf_loader, txt_loader, listdir_with_allowed_type, get_file_md5_hex
from utils.logger_handler import logger
from langchain_core.documents import Document

class VectorStoreService:
    def __init__(self):
        self.vector_store = Chroma(
            collection_name=chroma_conf["collection_name"],
            embedding_function=embed_model,
            persist_directory=chroma_conf["persist_directory"],
        )
        self.spliter = RecursiveCharacterTextSplitter(
            chunk_size=chroma_conf["chunk_size"],
            chunk_overlap=chroma_conf["chunk_overlap"],
            separators= chroma_conf["separators"],
            length_function=len,
        )


    def get_retriever(self):
        return self.vector_store.as_retriever(search_kwargs={"k": chroma_conf["k"]})


    def load_document(self):
        """
        Read documents from the data directory, embed them, and store them in the vector database.
        Compute file MD5 hashes to skip previously processed content.
        :return:
        """

        def check_md5_hex(md5_for_check: str):
            if not os.path.exists(get_abs_path(chroma_conf["md5_hex_store"])):
                # Create file
                open(get_abs_path(chroma_conf["md5_hex_store"]), "w", encoding="utf-8").close()
                return False            #Hash has not been processed

            with open(get_abs_path(chroma_conf["md5_hex_store"]), "r", encoding="utf-8") as f:
                for line in f.readlines():
                    line = line.strip()
                    if line == md5_for_check:
                      return True     #Hash has already been processed

                return False            #Hash has not been processed

        def save_md5_hex(md5_for_check:str):
            with open(get_abs_path(chroma_conf["md5_hex_store"]), "a", encoding="utf-8") as f:
                f.write(md5_for_check + "\n")


        def get_file_documents(read_path: str):
            if read_path.endswith("txt"):
                return txt_loader(read_path)

            if read_path.endswith("pdf"):
                return pdf_loader(read_path)

            return []

        allowed_files_path: list[str] = listdir_with_allowed_type(
            get_abs_path(chroma_conf["data_path"]),
            tuple(chroma_conf["allow_knowledge_file_type"]),
        )

        for path in allowed_files_path:
            # Get the file MD5 hash
            md5_hex = get_file_md5_hex(path)

            if check_md5_hex(md5_hex):
                logger.info(f"[Knowledge ingestion]{path} content is already in the knowledge base; skipping")
                continue

            try:
                documents: list[Document] = get_file_documents(path)

                if not documents:
                    logger.warning(f"[Knowledge ingestion]{path} contains no valid text; skipping")
                    continue

                split_document: list[Document] = self.spliter.split_documents(documents)

                if not split_document:
                    logger.warning(f"[Knowledge ingestion]{path} has no valid text after splitting; skipping")
                    continue

                #Insert the content into the vector store
                self.vector_store.add_documents(split_document)

                #Record the processed file hash to avoid loading the same content again
                save_md5_hex(md5_hex)

                logger.info(f"[Knowledge ingestion]{path} content loaded successfully")
            except Exception as e:
                # Set exc_info to True to log the traceback; False logs only the error message
                logger.error(f"[Knowledge ingestion]{path} loading failed: {str(e)}", exc_info=True)
                continue


if __name__ == "__main__":
    vs = VectorStoreService()

    vs.load_document()

    retriever = vs.get_retriever()
    res = retriever.invoke("lost navigation")
    for r in res:
        print(r.page_content)
        print("-"*20)