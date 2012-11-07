"""
### Markdown-Python-Ditaa

Based on mdx_graphviz.py, see it for details.

"""
import markdown
import markdown.preprocessors
import os
import shutil
import subprocess
import tempfile


class DitaaExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {'BINARY_PATH': "", 'WRITE_IMGS_DIR': "",
                       "BASE_IMG_LINK_DIR": "", "ARGUMENTS": ""}
        for key, value in configs:
            self.config[key] = value

    def reset(self):
        pass

    def extendMarkdown(self, md, md_globals):
        "Add DitaaExtension to the Markdown instance."
        md.registerExtension(self)
        self.parser = md.parser
        md.preprocessors.add('ditaa', DitaaPreprocessor(self), '_begin')


class DitaaPreprocessor(markdown.preprocessors.Preprocessor):
    """Find all ditaa blocks, generate images and inject image link to
    generated images.
    """

    def __init__(self, ditaa):
        self.ditaa = ditaa
        self.formatters = ["ditaa"]

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
        """Generates a graph from lines and returns a string containing n
        image link to created graph.
        """
        assert(kind in self.formatters)
        tmp = tempfile.NamedTemporaryFile()
        tmp.write("\n".join(lines))
        tmp.flush()
        cmd = "%s %s %s" % (
            os.path.join(self.ditaa.config["BINARY_PATH"], kind),
            self.ditaa.config["ARGUMENTS"], tmp.name)
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE, close_fds=True)
        p.wait()
        filepath = "%s%s%s.png" % (self.ditaa.config["WRITE_IMGS_DIR"],
                                   kind, n)
        shutil.copyfile(tmp.name + ".png", filepath)
        output_path = "%s%s%s.png" % (self.ditaa.config["BASE_IMG_LINK_DIR"],
                                      kind, n)
        return "![Ditaa chart %s](%s)" % (n, output_path)


def makeExtension(configs=None):
    return DitaaExtension(configs=configs)
