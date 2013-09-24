"""
### Markdown-Python-PlantUML

Based on mdx_graphviz.py, see it for details.

"""
import markdown
import markdown.preprocessors
import os
import shutil
import subprocess
import tempfile


class PlantUMLExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {'BINARY_PATH': "", 'WRITE_IMGS_DIR': "",
                       "BASE_IMG_LINK_DIR": "", "ARGUMENTS": ""}
        for key, value in configs:
            self.config[key] = value

    def reset(self):
        pass

    def extendMarkdown(self, md, md_globals):
        "Add PlantUMLExtension to the Markdown instance."
        md.registerExtension(self)
        self.parser = md.parser
        md.preprocessors.add('plantuml', PlantUMLPreprocessor(self), '_begin')


class PlantUMLPreprocessor(markdown.preprocessors.Preprocessor):
    """Find all plantuml blocks, generate images and inject image link to
    generated images.
    """

    def __init__(self, plantuml):
        self.plantuml = plantuml
        self.formatters = ["plantuml"]

    def run(self, lines):
        start_tags = ["<%s>" % x for x in self.formatters]
        end_tags = ["</%s>" % x for x in self.formatters]
        graph_n = 0
        new_lines = []
        block = []
        in_block = None
        for line in lines:
            if line in start_tags:
                assert(block == [])
                in_block = self.extract_format(line)
            elif line in end_tags:
                new_lines.append(self.graph(graph_n, in_block, block))
                graph_n = graph_n + 1
                block = []
                in_block = None
            elif in_block in self.formatters:
                block.append(line)
            else:
                new_lines.append(line)
        assert(block == [])
        return new_lines

    def extract_format(self, tag):
        fmt = tag[1:-1]
        assert(fmt in self.formatters)
        return fmt

    def graph(self, n, kind, lines):
        """Generates a graph from lines and returns a string containing an
        image link to created graph.
        """
        assert(kind in self.formatters)
        tmp = tempfile.NamedTemporaryFile()
        tmp.write("@startuml\n" + "\n".join(lines) + "\n@enduml\n")
        tmp.flush()
        cmd = "%s %s %s" % (
            os.path.join(self.plantuml.config["BINARY_PATH"], kind),
            self.plantuml.config["ARGUMENTS"], tmp.name)
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, close_fds=True)
        p.wait()
        filepath = "%s%s%s.png" % (self.plantuml.config["WRITE_IMGS_DIR"],
                                   kind, n)
        shutil.copyfile(tmp.name + ".png", filepath)
        output_path = "%s%s%s.png" % (
            self.plantuml.config["BASE_IMG_LINK_DIR"], kind, n)
        return "![PlantUML chart %s](%s)" % (n, output_path)


def makeExtension(configs=None):
    return PlantUMLExtension(configs=configs)
