import webapp2
import jinja2
import os, sys
import urllib2
from pygments import highlight
from pygments.lexers import PythonLexer, get_lexer_for_filename
from pygments.formatters import HtmlFormatter

class GithubLikeHtmlFormatter(HtmlFormatter):
    def __init__(self, **options):
        HtmlFormatter.__init__(self, **options)
        self.lineidprefix = options.get('lineidprefix', 'line')

    def wrap(self, source, outfile):
        return self._wrap_code(HtmlFormatter.wrap(self, source, outfile))

    def _wrap_code(self, source):
        line = self.linenostart - 1
        for i, t in source:
            if i == 1:
                line += 1
                t = "<div class='line' id='{}{}'>{}</div>".format(self.lineidprefix, line, t)
            yield i, t

class MainPage(webapp2.RequestHandler):
    def get(self):
        jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
        template = jinja_environment.get_template('index.html')
        
        values = dict()
        
        if 'url' in self.request.GET:
            url = self.request.GET['url']
            values['url'] = url
            try:
                req = urllib2.urlopen(url)
                encoding = req.headers['content-type'].split('charset=')[-1] if req.headers['content-type'].find('charset=') is not -1 else 0
                src = req.read() if encoding is 0 else unicode(req.read(), encoding)
                
                format_config = dict()
                if 'lineidprefix' in self.request.GET:
                    format_config['lineidprefix'] = self.request.GET['lineidprefix']
                if 'cssclass' in self.request.GET:
                    format_config['cssclass'] = self.request.GET['cssclass']
                
                values['highlighted'] = highlight(src, 
                                                  get_lexer_for_filename(url), 
                                                  GithubLikeHtmlFormatter(**format_config))
            except urllib2.URLError as e:
                values['error'] = 'URLError: {0}'.format(str(e))
            except urllib2.HTTPError as e:
                values['error'] = 'HTTPError: {0}'.format(str(e))
            
        
        self.response.out.write(template.render(values))

app = webapp2.WSGIApplication([('/', MainPage)])