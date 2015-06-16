def entropy(l):
      from math import log
      log2=lambda x:log(x)/log(2)
      total=len(l)
      counts={}
      for item in l:
        counts.setdefault(item,0)
        counts[item]+=1
      ent=0

      print(counts)
      
      for i in counts:
        p=float(counts[i])/total
        ent-=p*log2(p)
      return ent

print(entropy([[1,2],[1,23]]))


