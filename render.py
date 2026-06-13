"""Render the electronic-collections table to a static HTML string."""

import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

_TEMPLATES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates")
_env = Environment(
    loader=FileSystemLoader(_TEMPLATES),
    autoescape=select_autoescape(["html"]),
)


def render(records, count, time):
    """Render ``index.html`` with the given collection records, total
    count, and last-updated time, returning the HTML as a string."""
    template = _env.get_template("index.html")
    return template.render(data=records, count=count, time=time)
