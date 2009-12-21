#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from taskPaperParser import TaskPaperParserBase, NestedTaskPaperMixin, FlatTaskPaperMixin

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ SExpression Tools
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TaskPaperSExpressionBase(TaskPaperParserBase): 
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

class FlatTaskPaperSExpressions(FlatTaskPaperMixin, TaskPaperSExpressionBase):
    pass
class TaskPaperSExpressions(NestedTaskPaperMixin, TaskPaperSExpressionBase):
    pass

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    import os, sys
    from pprint import pprint

    for fn in sys.argv[1:]:
        builder = TaskPaperSExpressions()
        r = builder.read(open(fn, "rb"))
        pprint(r)

