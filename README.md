unset ROS_DISTRO
unset PYTHONPATH
python -c "import sys; sys.path = [p for p in sys.path if 'ros' not in p.lower()]"





# ollama_agent

## Ollama settings
ollama need to open localport
add OLLAMA_HOST=0.0.0.0:11434 

## weaviate query
- near_text
 :  find objects with the nearest vector to an input text.
- near_object : find similar objects to that object

### vecrot search options

- target_vector
   : restrict the query property
```python
response = reviews.query.near_text(
    query="a sweet German white wine",
    limit=2,
    target_vector="title_country",  # Specify the target vector for named vector collections
    return_metadata=MetadataQuery(distance=True)
)
```

- distance
    : set a similarity threshold between the search and target vectors
```python
response = jeopardy.query.near_text(
    query="animals in movies",
    distance=0.25, # max accepted distance
    return_metadata=MetadataQuery(distance=True)
)
```
- filters
    :narrow your search, for more specific results

### keyword search options
- query_properties
    : can be directed to only search a subset of object properties.

```python
response = jeopardy.query.bm25(
    query="safety",
    query_properties=["question"],
    return_metadata=MetadataQuery(score=True),
    limit=3
)
```