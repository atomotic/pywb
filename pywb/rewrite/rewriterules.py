from pywb.utils.dsrules import BaseRule

from regex_rewriters import RegexRewriter, CSSRewriter, XMLRewriter
from regex_rewriters import JSLinkAndLocationRewriter, JSLinkOnlyRewriter
from html_rewriter import HTMLRewriter
from header_rewriter import HeaderRewriter

import itertools

class RewriteRules(BaseRule):
    def __init__(self, url_prefix, config={}):
        super(RewriteRules, self).__init__(url_prefix, config)

        self.rewriters = {}

        #self._script_head_inserts = config.get('script_head_inserts', {})

        self.rewriters['header'] = config.get('header_class', HeaderRewriter)
        self.rewriters['css'] = config.get('css_class', CSSRewriter)
        self.rewriters['xml'] = config.get('xml_class', XMLRewriter)
        self.rewriters['html'] = config.get('html_class', HTMLRewriter)

        # Custom handling for js rewriting, often the most complex
        self.js_rewrite_location = config.get('js_rewrite_location', True)
        self.js_rewrite_location = bool(self.js_rewrite_location)

        # ability to toggle rewriting
        if self.js_rewrite_location:
            js_default_class = JSLinkAndLocationRewriter
        else:
            js_default_class = JSLinkOnlyRewriter

        # set js class, using either default or override from config
        self.rewriters['js'] = config.get('js_class', js_default_class)

        # add any regexs for js rewriter
        self._add_custom_regexs('js', config)

    def _add_custom_regexs(self, field, config):
        regexs = config.get(field + '_regexs')
        if not regexs:
            return

        rewriter_cls = self.rewriters[field]

        rule_def_tuples = RegexRewriter.parse_rules_from_config(regexs)

        def extend_rewriter_with_regex(urlrewriter):
            #import sys
            #sys.stderr.write('\n\nEXTEND: ' + str(rule_def_tuples))
            return rewriter_cls(urlrewriter, rule_def_tuples)

        self.rewriters[field] = extend_rewriter_with_regex