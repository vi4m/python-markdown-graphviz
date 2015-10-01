"""
### Markdown-Python-Graphviz

This module is an extention to [Python-Markdown][pymd] which makes it
possible to embed [Graphviz][gv] syntax into Markdown documents.

### Requirements

Using this module requires:
   * Python-Markdown
   * Graphviz (particularly ``dot``)

### Syntax

Wrap Graphviz definitions within a dot/neato/dotty/lefty tag.

An example document:

    This is some text above a graph.

    <dot>
    digraph a {
        nodesep=1.0;
        rankdir=LR;
        a -> b -> c ->d;
    }
    </dot>

    Some other text between two graphs.

    <neato>
    some graph in neato...
    </neato>

    This is also some text below a graph.

Note that the opening and closing tags should come at the beginning of
their lines and should be immediately followed by a newline.
    
### Usage

    import markdown
    md = markdown.Markdown(
            extensions=['graphviz'], 
            extension_configs={'graphviz' : {'DOT','/usr/bin/dot'}}
    )
    return md.convert(some_text)


[pymd]: http://www.freewisdom.org/projects/python-markdown/ "Python-Markdown"
[gv]: http://www.graphviz.org/ "Graphviz"

"""
import markdown, re, markdown.preprocessors, subprocess
import os
import hashlib

class GraphvizExtension(markdown.Extension):
    def __init__(self, configs):
        self.config = {'FORMAT':'png', 'BINARY_PATH':"", 'WRITE_IMGS_DIR':"", "BASE_IMG_LINK_DIR":""}
        for key, value in configs.iteritems():
            self.config[key] = value
    
    def reset(self):
        pass

    def extendMarkdown(self, md, md_globals):
        "Add GraphvizExtension to the Markdown instance."
        md.registerExtension(self)
        self.parser = md.parser
        md.preprocessors.add('graphviz', GraphvizPreprocessor(self), '_begin')

class GraphvizPreprocessor(markdown.preprocessors.Preprocessor):
    "Find all graphviz blocks, generate images and inject image link to generated images."

    def __init__ (self, graphviz):
        self.graphviz = graphviz
        self.formatters = ["seqdiag", "blockdiag", "actdiag", "nwdiag", "dot", "neato", "lefty", "dotty"]
        self.blockdiag_formatters = self.formatters[0:4]

    def run(self, lines):
        start_tags = [ "<%s>" % x for x in self.formatters ]
        end_tags = [ "</%s>" % x for x in self.formatters ]
        graph_n = 0
        new_lines = []
        block = []
        in_block = None
        for line in lines:
            line = line.rstrip('\r')
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
        #if block == []:
        #    raise UserWarning("Empty dot block in file near %s"  % lines)
        assert(block == [])
        return new_lines

    def extract_format(self, tag):
        format = tag[1:-1]
        assert(format in self.formatters)
        return format

    def graph(self, n, type, lines):
        "Generates a graph from lines and returns a string containing n image link to created graph."
        assert(type in self.formatters)        
        if type in self.blockdiag_formatters:
            cmd = "%s -o /dev/stdout -" % (type,)
        else: 
            cmd = "%s%s -T%s" % (self.graphviz.config["BINARY_PATH"],
                             type,
                             self.graphviz.config["FORMAT"])
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, close_fds=True)
        #(child_stdin, child_stdout) = (p.stdin, p.stdout) 
        contents = "\n".join(lines)
        p.stdin.write(contents)
        digest = str(hashlib.sha256(contents).hexdigest())
        p.stdin.close()
        p.wait()
        output_dir = os.path.join(self.graphviz.config['mkdocs_site_dir'], self.graphviz.config["WRITE_IMGS_DIR"])
        print(output_dir)
        filename = "%s.%s" % (digest, self.graphviz.config["FORMAT"])
        filepath = os.path.join(output_dir, filename)
        print(filepath)
        if not os.path.exists(output_dir):
          os.mkdir(output_dir)
        fout = open(filepath, 'w')
        fout.write(p.stdout.read())
        fout.close()
        img_link = os.path.join(self.graphviz.config["BASE_IMG_LINK_DIR"], filename)
        return "![Graphviz chart %s](%s)" % (n, img_link)

def makeExtension(configs=None):
    return GraphvizExtension(configs=configs)
