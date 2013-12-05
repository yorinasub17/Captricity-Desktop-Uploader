'''
Contains all the utility funcs.
'''
import re
import sip

def delete_layout(layout):
    if layout is None: return
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i).widget()
        if item is not None:
            item.setParent(None)
        else:
            delete_layout(layout.itemAt(i).layout())
    sip.delete(layout)
    del layout
    
def ident(x):
    return x

def natural_sort(file_list, get_filename=ident):
    def natural_string_compare(a, b):
        str1 = get_filename(a)
        str2 = get_filename(b)
        str_chunks1 = [int(x) if (x is not None and x.isdigit()) else x for x in re.split('(\d+)|[-_\.\/]', str1.lower())]
        str_chunks2 = [int(x) if (x is not None and x.isdigit()) else x for x in re.split('(\d+)|[-_\.\/]', str2.lower())]
        return cmp(str_chunks1, str_chunks2)
    return sorted(file_list, cmp=natural_string_compare)


