import re
from dataclasses import dataclass

@dataclass
class Snippet:
    trigger: str      
    expansion: str 
    case_sensitive: bool = False


class SnippetExpander:
    def __init__(self, snippets: list[Snippet] | None = None):
        self._snippets: dict[str, Snippet] = {}
        if snippets:
            for snippet in snippets:
                self.add(snippet)

    def add(self, snippet: Snippet) -> None:
        key = snippet.trigger if snippet.case_sensitive else snippet.trigger.lower()
        self._snippets[key] = snippet

    def remove(self, trigger: str) -> None:
        self._snippets.pop(trigger.lower(), None)

    def expand(self, text: str) -> str:
        """Replace every whole-word match of a trigger with its expansion."""
        if not text or not self._snippets:
            return text

        def replace_match(match: re.Match) -> str:
            word = match.group(0)
            lookup_key = word if word in self._snippets else word.lower()
            snippet = self._snippets.get(lookup_key)
            return snippet.expansion if snippet else word
        pattern = r"\b\w+\b"
        return re.sub(pattern, replace_match, text)