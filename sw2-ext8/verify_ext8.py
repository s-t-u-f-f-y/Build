from pathlib import Path
import sys,re
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
errors=[]

def txt(rel):
 p=root/rel
 if not p.exists(): errors.append(f'missing: {rel}'); return ''
 return p.read_text(encoding='utf-8-sig',errors='replace')

main=txt('binary/src/main.cpp')
if '2.0.2-ext8' not in main: errors.append('module version is not ext8')
for rel in ['binary/src/shaders/VertexDeformation.h','binary/src/shaders/VertexDeformationVertexLit.h']:
 s=txt(rel)
 for i in range(1,9):
  for k in ('CENTER','ANGLE','SCALE'):
   token=f'ELLIPSOID_{k}_{i}'
   if token not in s: errors.append(f'{rel}: missing {token}')
 if 'packed[40]' not in s: errors.append(f'{rel}: missing 40-float pack')
 if ', packed, 10' not in s: errors.append(f'{rel}: expected 10 vertex constant registers')

vs=txt('binary/src/shaders/hlsl/VertexDeformationVertexLit_vs30.hlsl')
ps=txt('binary/src/shaders/hlsl/VertexDeformationVertexLit_ps30.hlsl')
uvs=txt('binary/src/shaders/hlsl/VertexDeformation_vs30.hlsl')
ups=txt('binary/src/shaders/hlsl/VertexDeformation_ps30.hlsl')
for i in range(10):
 if f'g_EP{i}' not in vs: errors.append(f'VertexLit VS missing g_EP{i}')
 if f'g_EP{i}' not in uvs: errors.append(f'Unlit VS missing g_EP{i}')
for rel,s in [('VertexLit VS',vs),('VertexLit PS',ps)]:
 if 'woundData01' in s or 'woundData2' in s: errors.append(f'{rel}: old 3-wound interpolator layout still present')
if 'ConsiderEllipsoid8' not in vs: errors.append('VertexLit VS: 8-wound selector missing')
if uvs.count('Consider(p,') != 8: errors.append(f'Unlit VS: expected 8 Consider calls, got {uvs.count("Consider(p,")}')
if vs.count('ConsiderEllipsoid8(') < 9: errors.append('VertexLit VS: expected helper + 8 calls')
if 'i.woundTail.w' in ps: errors.append('VertexLit PS: old projPosZ channel remains')

for rel,s in [('VertexLit VS',vs),('VertexLit PS',ps),('Unlit VS',uvs),('Unlit PS',ups)]:
 if s.count('{') != s.count('}'): errors.append(f'{rel}: unbalanced braces')

if errors:
 print('EXT8 VERIFY FAILED')
 for e in errors: print(' -',e)
 sys.exit(1)
print('EXT8 VERIFY OK: source exposes 8 slots and uses nearest-wound VS->PS layout.')
