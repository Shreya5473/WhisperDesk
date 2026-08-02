from src.whisperdesk.core.snippets.expander import Snippet, SnippetExpander

expander = SnippetExpander([
    Snippet(trigger="eml", expansion="shreya@example.com"),
    Snippet(trigger="addr", expansion="Dubai, UAE"),
])

text = "please send it to my eml, my addr is on the form"
print(expander.expand(text))