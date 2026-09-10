import sys
sys.path.insert(0,sys.argv[1])
from core import page
for items in [[],[1],[1,2,3],tuple(range(7))]:
 for offset in [-5,-1,0,1,5,9]:
  for limit in [-3,0,1,2,3,20]:
   before=list(items);out=page(items,offset,limit)
   assert isinstance(out,list)
   assert out==list(items)[max(0,offset):max(0,offset)+max(0,limit)]
   assert list(items)==before
   assert out is not items
print('144 held-out boundary cases passed')
