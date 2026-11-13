import sys
M={'#14202B':'#1A1A1A','#EEF4F6':'#F2F4F9','#9FB3BA':'#A7B0C0','#0E1A26':'#0F1E5A','#0E8FA3':'#1428A0','#9FDBE6':'#AFC0F5','#3d4c5c':'#3a4250','#d7e6ef':'#d9e0f2','#2E9E6B':'#3B63E0','#F5B942':'#F5A800','#5D6F84':'#5F6B7A','rgba(159,219,230':'rgba(175,192,245','#cfe1ee':'#d9e0f2','#2EC4D6':'#3B9BFF'}
t=open(sys.argv[1]).read()
for a,b in M.items(): t=t.replace(a,b)
t=t.replace('</style>','.cap{display:none}</style>')
open(sys.argv[2],'w').write(t)
