from llama_index.readers.web import TrafilaturaWebReader

loader = TrafilaturaWebReader()
documents = loader.load_data(urls=["https://google.com"])


print(documents)


from llama_index.readers.web import NewsArticleReader

loader = NewsArticleReader()
documents = loader.load_data(urls=["https://google.com"] )
print(documents)


