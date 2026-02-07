import docx
import sys

def read_docx(file_path):
    try:
        doc = docx.Document(file_path)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        return str(e)

if __name__ == "__main__":
    file_path = "/Users/jiajun/Desktop/Crypto/Web3/20260207 Memory Hackathon/加密货币历史行情网站 产品需求文档（PRD）.docx"
    content = read_docx(file_path)
    print(content)
