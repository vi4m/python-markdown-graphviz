# coding: utf-8
import re
import markdown

"""Replace all '**text**' with '<b>text</b'. Because we are a postprocessor,
we assume that the only occurences left in the text are inside code blocks.

To avoid undesired behaviour, there is no multiline support. So you have
to add the bold asterisks on every line you want to be formatted bold.
"""

BOLDCODE_RE = r'(\*\*)(.*?)(\*\*)'


class BoldCodeExtension(markdown.Extension):

    def __init__(self, configs):
        for key, value in configs:
            self.setConfig(key, value)

    def extendMarkdown(self, md, md_globals):
        md.postprocessors.add('boldcode', BoldCodeProcessor(md), '_begin')
        md.registerExtension(self)

    def reset(self):
        pass


class BoldCodeProcessor(markdown.postprocessors.Postprocessor):
    def run(self, text):

        new_text = re.sub(BOLDCODE_RE, r'<b>\2</b>', text)
        return new_text


def makeExtension(configs=None):
    return BoldCodeExtension(configs=configs)
