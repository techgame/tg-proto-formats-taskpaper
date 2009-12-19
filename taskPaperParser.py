#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import re
import bisect
from functools import partial

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def reFlatten(matcher, useGroups=True):
    if isinstance(matcher, basestring):
        return matcher

    parts = []
    for e in matcher:
        if isinstance(e, tuple):
            e = (e[0], reFlatten(e[1], useGroups))
            if useGroups:
                parts.append('(?P<%s>%s)' % e)
                continue
            else:
                e = e[1]

        parts.append(e)
    return ''.join(parts)
 
def structureEntry(*args):
    return [('indent', r'\s*')] + list(args)
textContent = ('text', r'\S.*')

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TaskPaperScanner(object):
    structure = [
        ('task',    structureEntry(r'- ', textContent)),
        ('project', structureEntry(textContent, r':\s*$')),
        ('note',    structureEntry(textContent)),
        ]
        
    tag = [
        ('tagEx',   [r'@', ('tag', r'\w+'), r'\(', ('arg', r'[^()]*'), r'\)']),
        ('tag',     [r'@', ('tag', r'\w+'), r'']),
        (None, r'([^@]*(@\W)?)*')]

    def __init__(self):
        self.scanPaper = self.compileScanner(self.structure)
        self.scanTag = self.compileScanner(self.tag)

    def compileScanner(self, exprList):
        lst = []
        for name, expr in exprList:
            expr = reFlatten(expr, True)

            if name:
                fn = getattr(self, '_on_'+name)
                fn = partial(fn, expr=re.compile(expr))
            else: fn = None

            lst.append((expr, fn))
        return re.Scanner(lst)

    def parse(self, line):
        return self.scanPaper.scan(line)[0]
    __call__ = parse

    def _on_task(self, scanner, item, expr):
        info = expr.match(item).groupdict()
        tags = self.scanTag.scan(item)[0]
        if tags: info['tags'] = tags
        return ('task', info)
    def _on_project(self, scanner, item, expr):
        info = expr.match(item).groupdict()
        tags = self.scanTag.scan(item)[0]
        if tags: info['tags'] = tags
        return ('project', info)
    def _on_note(self, scanner, item, expr):
        info = expr.match(item).groupdict()
        tags = self.scanTag.scan(item)[0]
        if tags: info['tags'] = tags
        return ('note', info)

    def _on_tag(self, scanner, item, expr):
        info = expr.match(item).groupdict()
        return ('tag', info)
    def _on_tagEx(self, scanner, item, expr):
        info = expr.match(item).groupdict()
        return ('tag', info)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TaskPaperParserBase(object):
    TaskPaperScanner = TaskPaperScanner

    def __init__(self):
        self.scanner = self.TaskPaperScanner()

    def reset(self):
        self._roots = []
        self._projects = []
        self._tasks = []

    def read(self, file, reset=True):
        if reset:
            self.reset()

        roots = self._roots
        for line in file:
            self.feed(line, roots)
        return roots

    def feed(self, line, roots=None):
        if roots is None:
            roots = self._roots
        for kind, info in self.scanner(line):
            level, item = self._buildItem(kind, info)
            parent = self._findParent(level, item, kind)
            self._assignParent(item, parent, roots)
        return roots

    def _buildItem(self, item):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))
    def _assignParent(self, item, parent, roots):
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

    def _findParent(self, level, item, kind):
        entry = (level, item)

        projects = self._projects; tasks = self._tasks
        pidx = bisect.bisect(projects, entry)
        tidx = bisect.bisect(tasks, entry)
        if pidx and entry[0] == projects[pidx-1][0]:
            pidx -= 1
        if tidx and entry[0] == tasks[tidx-1][0]:
            tidx -= 1

        del projects[pidx+1:] # pop any projects more nested

        if 'project' == kind:
            projects[pidx:] = [entry]
            del tasks[:] # clear all tasks for a new project

            if pidx > 0:
                parent = projects[pidx-1]
            else: parent = None

        else:
            if 'task' == kind:
                tasks[tidx:] = [entry]
            else:
                del tasks[tidx+1:] # pop any tasks more nested

            if tidx > 0:
                parent = tasks[tidx-1]
            elif pidx >= len(projects): 
                parent = projects[-1]
            else: parent = projects[pidx]


        if parent is None:
            return None
        else:
            return parent[1]

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TaskPaperParser(TaskPaperParserBase): 
    def _buildItem(self, kind, info):
        level = len(info.pop('indent', ''))
        if kind != 'note':
            item = (kind, info, [])
        else: item = (kind, info)
        return level, item

    def _assignParent(self, item, parent, roots):
        if parent is None:
            roots.append(item)
        else: 
            parent[-1].append(item)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    import os, sys
    from pprint import pprint

    def testScanner(fn):
        scan = TaskPaperScanner()
        for line in open(fn, "rb"):
            r = scan(line)[0]
            for k, text, info, tags in r:
                print '%s: %s' % (k, text)
                for tag, name, arg in tags:
                    if arg:
                        print '  @%s(%s)' % (name,arg)
                    else:
                        print '  @%s' % (name,)
                if tags: print
    
    def testParser(fn):
        builder = TaskPaperParser()
        r = builder.read(open(fn, "rb"))
        pprint(r)

    for fn in sys.argv[1:]:
        testParser(fn)

