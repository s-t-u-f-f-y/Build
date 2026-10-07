from pathlib import Path
import re, sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()

def read(rel):
    return (ROOT / rel).read_text(encoding='utf-8-sig')

def write(rel, s):
    (ROOT / rel).write_text(s, encoding='utf-8', newline='\n')
    print('pack4 fixed', rel)

def sub1(s, pat, repl, label):
    out, n = re.subn(pat, repl, s, count=1, flags=re.S)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, got {n}')
    return out

def cpp_pack(prefix):
    N = prefix
    return f'''
\t\tconst int centerParams[8] = {{
\t\t\tELLIPSOID_CENTER_1, ELLIPSOID_CENTER_2, ELLIPSOID_CENTER_3, ELLIPSOID_CENTER_4,
\t\t\tELLIPSOID_CENTER_5, ELLIPSOID_CENTER_6, ELLIPSOID_CENTER_7, ELLIPSOID_CENTER_8
\t\t}};
\t\tconst int angleParams[8] = {{
\t\t\tELLIPSOID_ANGLE_1, ELLIPSOID_ANGLE_2, ELLIPSOID_ANGLE_3, ELLIPSOID_ANGLE_4,
\t\t\tELLIPSOID_ANGLE_5, ELLIPSOID_ANGLE_6, ELLIPSOID_ANGLE_7, ELLIPSOID_ANGLE_8
\t\t}};
\t\tconst int scaleParams[8] = {{
\t\t\tELLIPSOID_SCALE_1, ELLIPSOID_SCALE_2, ELLIPSOID_SCALE_3, ELLIPSOID_SCALE_4,
\t\t\tELLIPSOID_SCALE_5, ELLIPSOID_SCALE_6, ELLIPSOID_SCALE_7, ELLIPSOID_SCALE_8
\t\t}};
\t\tfloat packed[32] = {{ 0.0f }};
\t\tfor (int wound = 0; wound < 8; ++wound)
\t\t{{
\t\t\tconst float* c = params[centerParams[wound]]->GetVecValue();
\t\t\tconst float* a = params[angleParams[wound]]->GetVecValue();
\t\t\tconst float* r = params[scaleParams[wound]]->GetVecValue();

\t\t\tconst float cx = floor({N}NormCenter(c[0]) * 4095.0f + 0.5f);
\t\t\tconst float cy = floor({N}NormCenter(c[1]) * 4095.0f + 0.5f);
\t\t\tconst float cz = floor({N}NormCenter(c[2]) * 4095.0f + 0.5f);
\t\t\tconst float ax = floor({N}NormAngle(a[0]) * 1023.0f + 0.5f);
\t\t\tconst float ay = floor({N}NormAngle(a[1]) * 1023.0f + 0.5f);
\t\t\tconst float az = floor({N}NormAngle(a[2]) * 1023.0f + 0.5f);
\t\t\tconst float rx = floor({N}NormRadius(r[0]) * 255.0f + 0.5f);
\t\t\tconst float ry = floor({N}NormRadius(r[1]) * 255.0f + 0.5f);
\t\t\tconst float rz = floor({N}NormRadius(r[2]) * 255.0f + 0.5f);

\t\t\tconst int o = wound * 4;
\t\t\tpacked[o + 0] = cx + cy * 4096.0f;
\t\t\tpacked[o + 1] = cz + ax * 4096.0f;
\t\t\tpacked[o + 2] = ay + az * 1024.0f;
\t\t\tpacked[o + 3] = rx + ry * 256.0f + rz * 65536.0f;
\t\t}}
'''

# C++: replace old 40-float/10-register block with exact 32-float/8-register block.
for rel, prefix, base in [
    ('binary/src/shaders/VertexDeformation.h', '', 'VERTEX_SHADER_SHADER_SPECIFIC_CONST_0'),
    ('binary/src/shaders/VertexDeformationVertexLit.h', 'SW2VD', 'VERTEX_SHADER_SHADER_SPECIFIC_CONST_4')
]:
    s = read(rel)
    pat = r'\t\tconst int centerParams\[8\] = \{.*?pShaderAPI->SetVertexShaderConstant\(\s*' + re.escape(base) + r', packed, 10\);\s*'
    repl = cpp_pack(prefix) + f'''\t\tpShaderAPI->SetVertexShaderConstant(
\t\t\t{base}, packed, 8);

'''
    s = sub1(s, pat, repl, rel + ' packed constants')
    write(rel, s)

DECODE = r'''void DecodeEllipsoid(float f0,float f1,float f2,float f3,out float3 c,out float3 e,out float3 r)
{
    float cx=fmod(f0,4096.0), cy=floor(f0/4096.0);
    float cz=fmod(f1,4096.0), ax=floor(f1/4096.0);
    float ay=fmod(f2,1024.0), az=floor(f2/1024.0);
    float rx=fmod(f3,256.0);
    float rt=floor(f3/256.0);
    float ry=fmod(rt,256.0), rz=floor(rt/256.0);
    c=float3(cx,cy,cz)*(1000.0/4095.0)-500.0;
    e=float3(ax,ay,az)*(WOUND_RANGE_ANGLE/1023.0);
    r=float3(rx,ry,rz)*(WOUND_RANGE_RADIUS/255.0);
}'''

# Unlit VS.
rel='binary/src/shaders/hlsl/VertexDeformation_vs30.hlsl'
s=read(rel)
s=sub1(s,
       r'const float4 g_EP0.*?const float4 g_EP9[^\n]*',
       '\n'.join([f'const float4 g_EP{i} : register( SHADER_SPECIFIC_CONST_{i} );' for i in range(8)]),
       'unlit constants')
s=sub1(s, r'void DecodeEllipsoid\(.*?\n\}', DECODE, 'unlit decoder')
s=s.replace('void Consider(float3 p,float f0,float f1,float f2,float f3,float f4,',
            'void Consider(float3 p,float f0,float f1,float f2,float f3,')
s=s.replace('DecodeEllipsoid(f0,f1,f2,f3,f4,c,e,r);',
            'DecodeEllipsoid(f0,f1,f2,f3,c,e,r);')
old_calls = '\n'.join([
'    Consider(p,g_EP0.x,g_EP0.y,g_EP0.z,g_EP0.w,g_EP1.x,bestPos,bestWd,bestDist);',
'    Consider(p,g_EP1.y,g_EP1.z,g_EP1.w,g_EP2.x,g_EP2.y,bestPos,bestWd,bestDist);',
'    Consider(p,g_EP2.z,g_EP2.w,g_EP3.x,g_EP3.y,g_EP3.z,bestPos,bestWd,bestDist);',
'    Consider(p,g_EP3.w,g_EP4.x,g_EP4.y,g_EP4.z,g_EP4.w,bestPos,bestWd,bestDist);',
'    Consider(p,g_EP5.x,g_EP5.y,g_EP5.z,g_EP5.w,g_EP6.x,bestPos,bestWd,bestDist);',
'    Consider(p,g_EP6.y,g_EP6.z,g_EP6.w,g_EP7.x,g_EP7.y,bestPos,bestWd,bestDist);',
'    Consider(p,g_EP7.z,g_EP7.w,g_EP8.x,g_EP8.y,g_EP8.z,bestPos,bestWd,bestDist);',
'    Consider(p,g_EP8.w,g_EP9.x,g_EP9.y,g_EP9.z,g_EP9.w,bestPos,bestWd,bestDist);'])
new_calls = '\n'.join([f'    Consider(p,g_EP{i}.x,g_EP{i}.y,g_EP{i}.z,g_EP{i}.w,bestPos,bestWd,bestDist);' for i in range(8)])
if old_calls not in s: raise SystemExit('unlit calls: old mapping not found')
s=s.replace(old_calls,new_calls,1)
write(rel,s)

# VertexLit VS.
rel='binary/src/shaders/hlsl/VertexDeformationVertexLit_vs30.hlsl'
s=read(rel)
s=sub1(s,
       r'const float4 g_EP0.*?const float4 g_EP9[^\n]*',
       '\n'.join([f'const float4 g_EP{i} : register( SHADER_SPECIFIC_CONST_{4+i} );' for i in range(8)]),
       'vertexlit constants')
decode8 = DECODE.replace('DecodeEllipsoid(', 'DecodeEllipsoid8(')
s=sub1(s, r'void DecodeEllipsoid8\(.*?\n\}', decode8, 'vertexlit decoder')
s=s.replace('void ConsiderEllipsoid8(float3 p,float f0,float f1,float f2,float f3,float f4,',
            'void ConsiderEllipsoid8(float3 p,float f0,float f1,float f2,float f3,')
s=s.replace('DecodeEllipsoid8(f0,f1,f2,f3,f4,c,e,r);',
            'DecodeEllipsoid8(f0,f1,f2,f3,c,e,r);')
old = '\n'.join([
'\tConsiderEllipsoid8(modelPos,g_EP0.x,g_EP0.y,g_EP0.z,g_EP0.w,g_EP1.x,selectedDpos,selectedWd,selectedDnormal,bestDist);',
'\tConsiderEllipsoid8(modelPos,g_EP1.y,g_EP1.z,g_EP1.w,g_EP2.x,g_EP2.y,selectedDpos,selectedWd,selectedDnormal,bestDist);',
'\tConsiderEllipsoid8(modelPos,g_EP2.z,g_EP2.w,g_EP3.x,g_EP3.y,g_EP3.z,selectedDpos,selectedWd,selectedDnormal,bestDist);',
'\tConsiderEllipsoid8(modelPos,g_EP3.w,g_EP4.x,g_EP4.y,g_EP4.z,g_EP4.w,selectedDpos,selectedWd,selectedDnormal,bestDist);',
'\tConsiderEllipsoid8(modelPos,g_EP5.x,g_EP5.y,g_EP5.z,g_EP5.w,g_EP6.x,selectedDpos,selectedWd,selectedDnormal,bestDist);',
'\tConsiderEllipsoid8(modelPos,g_EP6.y,g_EP6.z,g_EP6.w,g_EP7.x,g_EP7.y,selectedDpos,selectedWd,selectedDnormal,bestDist);',
'\tConsiderEllipsoid8(modelPos,g_EP7.z,g_EP7.w,g_EP8.x,g_EP8.y,g_EP8.z,selectedDpos,selectedWd,selectedDnormal,bestDist);',
'\tConsiderEllipsoid8(modelPos,g_EP8.w,g_EP9.x,g_EP9.y,g_EP9.z,g_EP9.w,selectedDpos,selectedWd,selectedDnormal,bestDist);'])
new = '\n'.join([f'\tConsiderEllipsoid8(modelPos,g_EP{i}.x,g_EP{i}.y,g_EP{i}.z,g_EP{i}.w,selectedDpos,selectedWd,selectedDnormal,bestDist);' for i in range(8)])
if old not in s: raise SystemExit('vertexlit calls: old mapping not found')
s=s.replace(old,new,1)
write(rel,s)

print('EXT8 pack4 applied: 8 wounds fit exactly in 8 float4 registers.')
