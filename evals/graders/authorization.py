import sys,copy
sys.path.insert(0,sys.argv[1])
from core import get_document
records={'a':{'id':'a','title':'A','owner_id':'alice','secret':'private'},'b':{'id':'b','title':'B','owner_id':'bob'},'orphan':{'id':'orphan','title':'Orphan'}}
before=copy.deepcopy(records)
for actor in [None,'',0,False,[],{}]:
 for key in ['a','absent','orphan']:
  assert get_document(records,actor,key)==(401,{'error':'unauthorized'})
for key in ['b','absent','orphan']:
 assert get_document(records,'alice',key)==(404,{'error':'not_found'})
assert get_document(records,'alice','a')==(200,{'id':'a','title':'A'})
assert records==before
print('22 held-out authorization cases and immutability passed')
