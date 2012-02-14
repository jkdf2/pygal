# -*- coding: utf-8 -*-
import os
from lxml import etree
from pygal.util import template
from math import cos, sin, pi


class Svg(object):
    """Svg object"""
    ns = 'http://www.w3.org/2000/svg'

    def __init__(self, graph):
        self.graph = graph
        self.root = etree.Element(
            "{%s}svg" % self.ns,
            attrib={
                'viewBox': '0 0 %d %d' % (self.graph.width, self.graph.height)
            },
            nsmap={
                None: self.ns,
                'xlink': 'http://www.w3.org/1999/xlink',
            })
        self.root.append(etree.Comment(u'Generated with pygal ©Kozea 2012'))
        self.root.append(etree.Comment(u'http://github.com/Kozea/pygal'))
        self.defs = self.node(tag='defs')
        self.add_style(self.graph.base_css or os.path.join(
            os.path.dirname(__file__), 'css', 'graph.css'))

    def add_style(self, css):
        style = self.node(self.defs, 'style', type='text/css')
        with open(css) as f:
            style.text = template(
                f.read(),
                style=self.graph.style,
                font_sizes=self.graph.font_sizes,
                hidden='y' if self.graph.horizontal else 'x',
                fill_opacity=self.graph.style.opacity
                if self.graph.fill else 0,
                fill_opacity_hover=self.graph.style.opacity_hover
                if self.graph.fill else 0)

    def node(self, parent=None, tag='g', attrib=None, **extras):
        if parent is None:
            parent = self.root
        attrib = attrib or {}
        attrib.update(extras)
        for key, value in attrib.items():
            if value is None:
                del attrib[key]
            elif not isinstance(value, basestring):
                attrib[key] = str(value)
            elif key == 'class_':
                attrib['class'] = attrib['class_']
                del attrib['class_']
        return etree.SubElement(parent, tag, attrib)

    def transposable_node(self, parent=None, tag='g', attrib=None, **extras):
        if self.graph.horizontal:
            for key1, key2 in (('x', 'y'), ('width', 'height')):
                attr1 = extras.get(key1, None)
                attr2 = extras.get(key2, None)
                extras[key1], extras[key2] = attr2, attr1
        return self.node(parent, tag, attrib, **extras)

    def format(self, xy):
        return '%f %f' % xy

    def line(self, node, coords, close=False, **kwargs):
        root = 'M%s L%s Z' if close else 'M%s L%s'
        origin = self.format(coords[0])
        line = ' '.join(map(self.format, coords[1:]))
        self.node(node, 'path',
                  d=root % (origin, line), **kwargs)

    def render(self):
        return etree.tostring(
            self.root, pretty_print=True,
            xml_declaration=True, encoding='utf-8')