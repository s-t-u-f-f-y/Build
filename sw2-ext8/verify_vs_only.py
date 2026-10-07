from pathlib import Path
import sys
root=Path(sys.argv[1] if len(sys.argv)>1 else '.').resolve()
errors=[]

def txt(rel):
    p=root/rel
    if not p.exists():
        errors.append('missing '+rel)
        return ''
    return p.read_text(encoding='utf-8-sig', errors='replace')

for rel in ['binary/src/shaders/VertexDeformation.h','binary/src/shaders/VertexDeformationVertexLit.h']:
    s=txt(rel)
    for i in range(1,9):
        for k in ('CENTER','ANGLE','SCALE'):
            if f'ELLIPSOID_{k}_{i}' not in s:
                errors.append(f'{rel}: missing {k}_{i}')
    if 'packed[40]' not in s or ', packed, 10' not in s:
        errors.append(f'{rel}: 8-wound packed constants missing')

uvs=txt('binary/src/shaders/hlsl/VertexDeformation_vs30.hlsl')
vvs=txt('binary/src/shaders/hlsl/VertexDeformationVertexLit_vs30.hlsl')
ups=txt('binary/src/shaders/hlsl/VertexDeformation_ps30.hlsl')
vps=txt('binary/src/shaders/hlsl/VertexDeformationVertexLit_ps30.hlsl')

for i in range(10):
    if f'g_EP{i}' not in uvs: errors.append(f'Unlit VS missing g_EP{i}')
    if f'g_EP{i}' not in vvs: errors.append(f'VertexLit VS missing g_EP{i}')

if uvs.count('Consider(p,') != 8:
    errors.append('Unlit VS does not process exactly 8 wounds')
if vvs.count('ConsiderEllipsoid8(') < 9:
    errors.append('VertexLit VS does not process 8 wounds')

for token in ('vWoundData0','vWoundData1','vWoundData2'):
    if token not in uvs: errors.append('Unlit stock PS interface missing '+token)
for token in ('woundData01','woundData2','woundTail'):
    if token not in vvs: errors.append('VertexLit stock PS interface missing '+token)

# Pixel shaders must stay on their stock 3-slot interface.
if 'vWoundData0' not in ups or 'vWoundData2' not in ups:
    errors.append('Unlit pixel shader is not stock-compatible')
if 'woundData01' not in vps or 'woundData2' not in vps:
    errors.append('VertexLit pixel shader is not stock-compatible')

if '2.0.2-ext8' not in txt('binary/src/main.cpp'):
    errors.append('EXT8 module version marker missing')

if errors:
    print('EXT8 VS-ONLY VERIFY FAILED')
    for e in errors: print(' - '+e)
    sys.exit(1)
print('EXT8 VS-ONLY VERIFY OK')
