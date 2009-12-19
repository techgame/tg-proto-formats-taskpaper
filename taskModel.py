#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Definitions 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TaskAtom(object):
    kind = None
    def isProject(self): return False
    def isTask(self): return False
    def isNote(self): return False
    def isTag(self): return False
    def accept(self, v, *args, **kw): 
        raise NotImplementedError('Subclass Responsibility: %r' % (self,))

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TaskTextAtom(TaskAtom):
    indent = ''
    text = None
    tags = ()
    children = None

    info = None
    def __init__(self, info):
        self.indent = info.pop('indent', '')
        self.text = info.pop('text')
        tags = info.pop('tags', None)
        if tags: self.tags = tags
        if info: self.info = info
        self.init()

    def init(self): pass
    def __repr__(self):
        return '<%s %r>' % (self.kind, self.text)

    _indent = ''
    def getIndent(self):
        return self._indent
    def setIndent(self, indent):
        indent = ''.join(sorted(indent))
        self._indent = indent
    indent = property(getIndent, setIndent)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TaskProject(TaskTextAtom): 
    kind = 'project'
    def isProject(self): return True
    def accept(self, v, *args, **kw): 
        return v.visitTaskProject(self, *args, **kw)

    def init(self):
        self.children = []
    def append(self, item):
        self.children.append(item)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TaskItem(TaskTextAtom): 
    kind = 'task'
    def isTask(self): return True
    def accept(self, v, *args, **kw): 
        return v.visitTaskItem(self, *args, **kw)

    def init(self):
        self.children = []
    def append(self, item):
        self.children.append(item)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TaskNote(TaskTextAtom): 
    kind = 'note'
    def isNote(self): return True
    def accept(self, v, *args, **kw): 
        return v.visitTaskNote(self, *args, **kw)

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TaskTag(TaskAtom): 
    kind = 'tag'
    tag = None
    arg = None
    def __init__(self, info):
        self.tag = info.pop('tag')
        arg = info.pop('arg', None)
        if arg is not None:
            self.arg = arg
        if info: self.info = info

    def __repr__(self):
        arg = self.arg
        if arg:
            return '<%s %s(%s)>' % (self.kind, self.tag, arg)
        else: return '<%s %s>' % (self.kind, self.tag)

    def isTag(self): return True
    def accept(self, v, *args, **kw): 
        return v.visitTaskTag(self, *args, **kw)

