#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Imports 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from taskPaperParser import TaskPaperParserBase, NestedTaskPaperMixin, FlatTaskPaperMixin
import taskModel

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Builder
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TaskPaperBuilderBase(TaskPaperParserBase):
    factoryMap = {
        'project': taskModel.TaskProject,
        'task': taskModel.TaskItem,
        'note': taskModel.TaskNote,
        'tag': taskModel.TaskTag, }

    def _buildItem(self, kind, info):
        self._buildTags(info)
        item = self.factoryMap[kind](info)
        return item.indent, item

    def _buildTags(self, info):
        tags = info.get('tags')
        if tags:
            FMap = self.factoryMap
            tags[:] = [FMap[k](t) for k,t in tags]
        return tags

    def _assignParent(self, item, parent, roots):
        if parent is None:
            roots.append(item)
        else: 
            parent.append(item)
    
class TaskPaperBuilder(NestedTaskPaperMixin, TaskPaperBuilderBase):
    pass

class FlatTaskPaperBuilder(TaskPaperBuilderBase):
    def _findParent(self, level, kind, item, roots):
        if roots and kind != 'project':
            return roots[-1]
        else: return None

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~ Main 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__=='__main__':
    import sys
    from pprint import pprint

    def printTreeList(r, level=0, I='  '):
        for e in r:
            if e.tags:
                print '%s%r %r' % (I*level, e, e.tags)
            else: print '%s%r' % (I*level, e)
            if e.children:
                printTreeList(e.children, level+1, I)

    for fn in sys.argv[1:]:
        builder = TaskPaperBuilder()
        #builder = FlatTaskPaperBuilder()
        r = builder.read(open(fn, "rb"))
        printTreeList(r)

