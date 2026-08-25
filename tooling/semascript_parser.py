
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union


class ParseError(Exception):
    """Raised when a SEMASCRIPT construction cannot be parsed."""


@dataclass
class Node:
    class_name: str
    root: str
    modifiers: List[str] = field(default_factory=list)
    roles: Dict[str, "Value"] = field(default_factory=dict)


Value = Union[Node, List["Value"], str]


class Parser:
    def __init__(self, text: str):
        self.text = text
        self.i = 0
        self.n = len(text)

    def parse(self) -> Node:
        self._skip_ws()
        node = self._parse_node()
        self._skip_ws()
        if self.i != self.n:
            raise ParseError(f"Unexpected trailing content at position {self.i}")
        return node

    def _parse_node(self) -> Node:
        self._skip_ws()
        self._expect("[")
        self._skip_ws()

        header = self._parse_identifier()
        if ":" not in header:
            raise ParseError(f"Header must contain CLASS:ROOT, got {header!r}")

        class_name, root = header.split(":", 1)
        if not class_name or not root:
            raise ParseError(f"Invalid CLASS:ROOT header: {header!r}")

        modifiers: List[str] = []
        roles: Dict[str, Value] = {}

        self._skip_ws()
        if self._peek() == "{":
            modifiers = self._parse_modifiers()
            self._skip_ws()

        if self._peek() == "<":
            roles = self._parse_roles()
            self._skip_ws()

        self._expect("]")
        return Node(class_name=class_name, root=root, modifiers=modifiers, roles=roles)

    def _parse_modifiers(self) -> List[str]:
        self._expect("{")
        mods: List[str] = []
        token = []
        while True:
            ch = self._peek()
            if ch is None:
                raise ParseError("Unterminated modifier block")
            if ch == "}":
                if token:
                    mods.append("".join(token).strip())
                self.i += 1
                break
            if ch in ", " or ch.isspace():
                if token:
                    mods.append("".join(token).strip())
                    token = []
                self.i += 1
                continue
            token.append(ch)
            self.i += 1
        return [m for m in mods if m]

    def _parse_roles(self) -> Dict[str, Value]:
        self._expect("<")
        roles: Dict[str, Value] = {}
        while True:
            self._skip_ws()
            if self._peek() == ">":
                self.i += 1
                break

            role = self._parse_identifier()
            self._skip_ws()
            self._expect("=")
            self._skip_ws()
            value = self._parse_value()
            roles[role] = value
            self._skip_ws()

            ch = self._peek()
            if ch == ";":
                self.i += 1
                continue
            if ch == ">":
                self.i += 1
                break
            raise ParseError(f"Expected ';' or '>' after role assignment at position {self.i}")
        return roles

    def _parse_value(self) -> Value:
        self._skip_ws()
        if self._peek() == "[":
            if self._looks_like_list():
                return self._parse_list()
            return self._parse_node()
        return self._parse_identifier()

    def _looks_like_list(self) -> bool:
        # Current position points to '['
        j = self.i + 1
        while j < self.n and self.text[j].isspace():
            j += 1
        if j >= self.n:
            return False
        # Empty list or list of nested values starts as a list
        return self.text[j] in {"[", "]"}

    def _parse_list(self) -> List[Value]:
            self._expect("[")
            values: List[Value] = []
            expect_value = True

            while True:
                self._skip_ws()
                ch = self._peek()
                if ch is None:
                    raise ParseError("Unterminated list")

                if ch == "]":
                    if expect_value and values:
                        raise ParseError("Trailing separator in list")
                    self.i += 1
                    break

                if not expect_value:
                    raise ParseError(f"Expected list separator at position {self.i}")

                value = self._parse_value()
                values.append(value)
                expect_value = False
                self._skip_ws()

                ch = self._peek()
                if ch in {";", ","}:
                    self.i += 1
                    expect_value = True
                    continue
                if ch == "]":
                    self.i += 1
                    break
                raise ParseError(f"Expected ';', ',' or ']' after list item at position {self.i}")
            return values

    def _parse_identifier(self) -> str:
        self._skip_ws()
        start = self.i
        allowed_stop = set("[]{}<>;=,\n\r\t ")
        while self.i < self.n and self.text[self.i] not in allowed_stop:
            self.i += 1
        if self.i == start:
            raise ParseError(f"Expected identifier at position {self.i}")
        return self.text[start:self.i]

    def _skip_ws(self) -> None:
        while self.i < self.n and self.text[self.i].isspace():
            self.i += 1

    def _peek(self) -> Optional[str]:
        if self.i >= self.n:
            return None
        return self.text[self.i]

    def _expect(self, char: str) -> None:
        if self._peek() != char:
            found = self._peek()
            raise ParseError(f"Expected {char!r} at position {self.i}, found {found!r}")
        self.i += 1


def parse(text: str) -> Node:
    return Parser(text).parse()
