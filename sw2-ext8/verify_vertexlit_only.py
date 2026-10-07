from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
errors=[]

def txt(rel):
    p=root/rel
    if not p.exists():
        errors.append('missing: '+rel)
        return ''
    return p.read_text(encoding='utf-8-sig',errors='replace')

h=txt('binary/src/shaders/VertexDeformationVertexLit.h')
for i in range(1,9):
    for k in ('CENTER','ANGLE','SCALE'):
        if f'ELLIPSOID_{k}_{i}' not in h:
            errors.append(f'VertexLit header missing ELLIPSOID_{k}_{i}')
if 'packed[32]' not in h or ', packed, 8' not in h:
    errors.append('VertexLit C++ does not use 32-float / 8-register packing')

vs=txt('binary/src/shaders/hlsl/VertexDeformationVertexLit_vs30.hlsl')
for i in range(8):
    if f'g_EP{i}' not in vs:
        errors.append(f'VertexLit VS missing g_EP{i}')
if 'g_EP8' in vs or 'g_EP9' in vs:
    errors.append('VertexLit VS still exceeds available registers')
if vs.count('ConsiderEllipsoid8(') < 9:
    errors.append('VertexLit VS does not process all 8 wounds')
for token in ('woundData01','woundData2','woundTail'):
    if token not in vs:
        errors.append('stock pixel-shader interface missing '+token)

ps=txt('binary/src/shaders/hlsl/VertexDeformationVertexLit_ps30.hlsl')
if 'woundData01' not in ps or 'woundData2' not in ps:
    errors.append('VertexLit stock pixel shader was not restored')

# Unlit path must remain stock and intentionally stays at three wounds.
unlit=txt('binary/src/shaders/VertexDeformation.h')
if 'ELLIPSOID_CENTER_4' in unlit:
    errors.append('Unlit shader should remain stock 3-slot')
if '2.0.2-ext8' not in txt('binary/src/main.cpp'):
    errors.append('module EXT8 version marker missing')

if errors:
    print('EXT8 VERTEXLIT VERIFY FAILED')
    for e in errors: print(' - '+e)
    sys.exit(1)
print('EXT8 VERTEXLIT VERIFY OK: 8 slots on NPC trigger path, stock unlit path preserved.')
