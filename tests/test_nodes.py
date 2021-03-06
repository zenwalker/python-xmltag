from xmltag.nodes import Node, XmlNode, TextNode, DocumentRoot
from unittest.mock import Mock
from nose import tools as test


def mock_document():
    doc = Mock()
    root = DocumentRoot(doc, 'html')
    doc.current_node = root
    doc.root_node = root

    def render_tag(tag, content, *args, **kwargs):
        return '<{t}>{c}</{t}>'.format(t=tag, c=content)

    doc.render_tag = render_tag
    doc.indent = None
    return doc


class TestNode:
    def test_with(self):
        doc = mock_document()
        with Node(doc) as html_node:
            test.assert_equal(doc.current_node, html_node)
        test.assert_equal(doc.current_node, doc.root_node)

    def test_append_to(self):
        doc = mock_document()
        root = XmlNode(doc, 'html')
        child = XmlNode(doc, 'body')
        child.append_to(root)
        test.assert_equal(root.child_nodes, [child])

    def test_is_last(self):
        doc = mock_document()
        root = XmlNode(doc, 'html')
        child_one = XmlNode(doc, 'head').append_to(root)
        child_two = XmlNode(doc, 'body').append_to(root)
        test.assert_false(child_one._is_last())
        test.assert_true(child_two._is_last())

    def test_remove(self):
        doc = mock_document()
        root = XmlNode(doc, 'html')
        child_node = XmlNode(doc, 'head')
        root.child_nodes.append(child_node)
        child_node.parent_node = root
        test.assert_in(child_node, root.child_nodes)
        child_node.remove()
        test.assert_not_in(child_node, root.child_nodes)


class TestXmlNode:
    def test_init(self):
        doc = mock_document()
        node = XmlNode(doc, 'html', attrs={'lang': 'en'})
        test.assert_equal(node.tag_name, 'html')
        test.assert_equal(node.attrs, {'lang': 'en'})

    def test_repr(self):
        node = XmlNode(mock_document(), 'html', attrs={'lang': 'ru'})
        test.assert_equal(repr(node), 'XmlNode(html, lang=ru)')

    def test_render(self):
        doc = mock_document()
        node = XmlNode(doc, 'html', attrs={'lang': 'en'})
        body = XmlNode(doc, 'body', content='hello world')
        node.child_nodes.append(body)
        test.assert_equal(node.render(), '<html><body>hello world</body></html>')

    def test_render_pretty(self):
        doc = mock_document()
        doc.indent = '..'
        node = XmlNode(doc, 'html')
        node.level = 0
        node.child_nodes.append(XmlNode(doc, 'body'))
        test.assert_equal(node.render(), '\n<html>\n..<body></body>\n</html>')

    def test_render_escape(self):
        doc = mock_document()
        node = XmlNode(doc, 'body', content='<div>"hello"</div>')
        test.assert_equal(node.render(), '<body>&lt;div&gt;"hello"&lt;/div&gt;</body>')
        node = XmlNode(doc, 'body', content='<div>"hello"</div>', safe=True)
        test.assert_equal(node.render(), '<body><div>"hello"</div></body>')


class TestTextNode:
    def setup(self):
        self.doc = mock_document()

    def test_render(self):
        node = TextNode(self.doc, 'hello world')
        test.assert_equal(node.render(), 'hello world')

    def test_render_escape(self):
        node = TextNode(self.doc, '<div>"hello"</div>')
        test.assert_equal(node.render(), '&lt;div&gt;"hello"&lt;/div&gt;')
        node = TextNode(self.doc, '<div>"hello"</div>', safe=True)
        test.assert_equal(node.render(), '<div>"hello"</div>')

    def test_repr(self):
        node = TextNode(self.doc, 'hello world')
        test.assert_equal(repr(node), 'TextNode(hello world)')
