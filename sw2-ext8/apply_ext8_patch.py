from pathlib import Path
import re, sys

ROOT = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()


def read(rel):
    p = ROOT / rel
    if not p.exists():
        raise SystemExit(f'Missing expected file: {p}')
    return p.read_text(encoding='utf-8-sig')


def write(rel, text):
    p = ROOT / rel
    p.write_text(text, encoding='utf-8', newline='\n')
    print('patched', rel)


def replace_once(text, old, new, label):
    n = text.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 exact match, found {n}')
    return text.replace(old, new, 1)


def sub_once(text, pattern, repl, label, flags=re.S):
    text2, n = re.subn(pattern, repl, text, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 regex match, found {n}')
    return text2

PARAMS_4_8 = '''
\tSHADER_PARAM(ELLIPSOID_CENTER_4, SHADER_PARAM_TYPE_VEC3, "[499 499 499]", "Ellipsoid center based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_ANGLE_4, SHADER_PARAM_TYPE_VEC3, "[0 0 0]", "Ellipsoid angle based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_SCALE_4, SHADER_PARAM_TYPE_VEC3, "[0.025 0.025 0.025]", "Ellipsoid scale based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_CENTER_5, SHADER_PARAM_TYPE_VEC3, "[499 499 499]", "Ellipsoid center based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_ANGLE_5, SHADER_PARAM_TYPE_VEC3, "[0 0 0]", "Ellipsoid angle based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_SCALE_5, SHADER_PARAM_TYPE_VEC3, "[0.025 0.025 0.025]", "Ellipsoid scale based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_CENTER_6, SHADER_PARAM_TYPE_VEC3, "[499 499 499]", "Ellipsoid center based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_ANGLE_6, SHADER_PARAM_TYPE_VEC3, "[0 0 0]", "Ellipsoid angle based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_SCALE_6, SHADER_PARAM_TYPE_VEC3, "[0.025 0.025 0.025]", "Ellipsoid scale based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_CENTER_7, SHADER_PARAM_TYPE_VEC3, "[499 499 499]", "Ellipsoid center based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_ANGLE_7, SHADER_PARAM_TYPE_VEC3, "[0 0 0]", "Ellipsoid angle based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_SCALE_7, SHADER_PARAM_TYPE_VEC3, "[0.025 0.025 0.025]", "Ellipsoid scale based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_CENTER_8, SHADER_PARAM_TYPE_VEC3, "[499 499 499]", "Ellipsoid center based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_ANGLE_8, SHADER_PARAM_TYPE_VEC3, "[0 0 0]", "Ellipsoid angle based on pre-skinned space")
\tSHADER_PARAM(ELLIPSOID_SCALE_8, SHADER_PARAM_TYPE_VEC3, "[0.025 0.025 0.025]", "Ellipsoid scale based on pre-skinned space")
'''

INIT_4_8_VERBOSE = '''
\tif (!params[ELLIPSOID_CENTER_4]->IsDefined()) params[ELLIPSOID_CENTER_4]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_ANGLE_4]->IsDefined()) params[ELLIPSOID_ANGLE_4]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_SCALE_4]->IsDefined()) params[ELLIPSOID_SCALE_4]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_CENTER_5]->IsDefined()) params[ELLIPSOID_CENTER_5]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_ANGLE_5]->IsDefined()) params[ELLIPSOID_ANGLE_5]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_SCALE_5]->IsDefined()) params[ELLIPSOID_SCALE_5]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_CENTER_6]->IsDefined()) params[ELLIPSOID_CENTER_6]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_ANGLE_6]->IsDefined()) params[ELLIPSOID_ANGLE_6]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_SCALE_6]->IsDefined()) params[ELLIPSOID_SCALE_6]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_CENTER_7]->IsDefined()) params[ELLIPSOID_CENTER_7]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_ANGLE_7]->IsDefined()) params[ELLIPSOID_ANGLE_7]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_SCALE_7]->IsDefined()) params[ELLIPSOID_SCALE_7]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_CENTER_8]->IsDefined()) params[ELLIPSOID_CENTER_8]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_ANGLE_8]->IsDefined()) params[ELLIPSOID_ANGLE_8]->SetVecValue(0.0f, 0.0f, 0.0f);
\tif (!params[ELLIPSOID_SCALE_8]->IsDefined()) params[ELLIPSOID_SCALE_8]->SetVecValue(0.0f, 0.0f, 0.0f);
'''

PACK8_BODY = '''
\t\tconst int centerParams[8] = {
\t\t\tELLIPSOID_CENTER_1, ELLIPSOID_CENTER_2, ELLIPSOID_CENTER_3, ELLIPSOID_CENTER_4,
\t\t\tELLIPSOID_CENTER_5, ELLIPSOID_CENTER_6, ELLIPSOID_CENTER_7, ELLIPSOID_CENTER_8
\t\t};
\t\tconst int angleParams[8] = {
\t\t\tELLIPSOID_ANGLE_1, ELLIPSOID_ANGLE_2, ELLIPSOID_ANGLE_3, ELLIPSOID_ANGLE_4,
\t\t\tELLIPSOID_ANGLE_5, ELLIPSOID_ANGLE_6, ELLIPSOID_ANGLE_7, ELLIPSOID_ANGLE_8
\t\t};
\t\tconst int scaleParams[8] = {
\t\t\tELLIPSOID_SCALE_1, ELLIPSOID_SCALE_2, ELLIPSOID_SCALE_3, ELLIPSOID_SCALE_4,
\t\t\tELLIPSOID_SCALE_5, ELLIPSOID_SCALE_6, ELLIPSOID_SCALE_7, ELLIPSOID_SCALE_8
\t\t};
\t\tfloat packed[40] = { 0.0f };
\t\tfor (int wound = 0; wound < 8; ++wound)
\t\t{
\t\t\tconst float* c = params[centerParams[wound]]->GetVecValue();
\t\t\tconst float* a = params[angleParams[wound]]->GetVecValue();
\t\t\tconst float* s = params[scaleParams[wound]]->GetVecValue();
\t\t\tconst int o = wound * 5;
\t\t\tpacked[o + 0] = SW2VDPack2(SW2VDNormCenter(c[0]), SW2VDNormCenter(c[1]));
\t\t\tpacked[o + 1] = SW2VDPack2(SW2VDNormCenter(c[2]), SW2VDNormAngle(a[0]));
\t\t\tpacked[o + 2] = SW2VDPack2(SW2VDNormAngle(a[1]), SW2VDNormAngle(a[2]));
\t\t\tpacked[o + 3] = SW2VDPack2(SW2VDNormRadius(s[0]), SW2VDNormRadius(s[1]));
\t\t\tpacked[o + 4] = SW2VDNormRadius(s[2]);
\t\t}
'''

PACK8_BODY_UNLIT = (PACK8_BODY
    .replace('SW2VDPack2', 'Pack2')
    .replace('SW2VDNormCenter', 'NormCenter')
    .replace('SW2VDNormAngle', 'NormAngle')
    .replace('SW2VDNormRadius', 'NormRadius'))

rel='binary/src/main.cpp'
s=read(rel)
s=replace_once(s, 'static const char* SIMPLE_WOUND_VERSION = "2.0.2";',
               'static const char* SIMPLE_WOUND_VERSION = "2.0.2-ext8";', 'main version')
write(rel,s)

rel='binary/src/shaders/VertexDeformation.h'
s=read(rel)
needle='\tSHADER_PARAM(ELLIPSOID_SCALE_3, SHADER_PARAM_TYPE_VEC3, "[0.025 0.025 0.025]", "Ellipsoid scale based on pre-skinned space")\n'
s=replace_once(s, needle, needle+PARAMS_4_8, 'VD params')
marker='''\tif (!params[ELLIPSOID_SCALE_3]->IsDefined())\n\t{\n\t\tparams[ELLIPSOID_SCALE_3]->SetVecValue(0.0, 0.0, 0.0);\n\t}\n'''
s=replace_once(s, marker, marker+INIT_4_8_VERBOSE, 'VD init')
pattern=r'\t\t// ---- 取 3 个椭球的原始参数 ----.*?(?=\t\tfloat bloodRange = params\[BLOOD_RANGE\]->GetFloatValue\(\);)'
replacement=PACK8_BODY_UNLIT + '\t\tpShaderAPI->SetVertexShaderConstant(\n\t\t\tVERTEX_SHADER_SHADER_SPECIFIC_CONST_0, packed, 10);\n\n'
s=sub_once(s,pattern,replacement,'VD pack')
write(rel,s)

rel='binary/src/shaders/VertexDeformationVertexLit.h'
s=read(rel)
s=replace_once(s, needle, needle+PARAMS_4_8, 'VDVL params')
marker='''\tif (!params[ELLIPSOID_SCALE_3]->IsDefined())\n\t\tparams[ELLIPSOID_SCALE_3]->SetVecValue(0.0f, 0.0f, 0.0f);\n'''
s=replace_once(s, marker, marker+INIT_4_8_VERBOSE, 'VDVL init')
pattern=r'\t\tconst float\* c1 = params\[ELLIPSOID_CENTER_1\]->GetVecValue\(\);.*?(?=\t\tfloat bloodRange = params\[BLOOD_RANGE\]->GetFloatValue\(\);)'
replacement=PACK8_BODY + '\t\tpShaderAPI->SetVertexShaderConstant(\n\t\t\tVERTEX_SHADER_SHADER_SPECIFIC_CONST_4, packed, 10);\n\n'
s=sub_once(s,pattern,replacement,'VDVL pack')
write(rel,s)

VD_VS = r'''// DYNAMIC: "SKINNING" "0..1"
// DYNAMIC: "COMPRESSED_VERTS" "0..1"
#include "common_vs_fxc.h"

static const bool g_bSkinning = SKINNING ? true : false;
const float4 g_EP0 : register( SHADER_SPECIFIC_CONST_0 );
const float4 g_EP1 : register( SHADER_SPECIFIC_CONST_1 );
const float4 g_EP2 : register( SHADER_SPECIFIC_CONST_2 );
const float4 g_EP3 : register( SHADER_SPECIFIC_CONST_3 );
const float4 g_EP4 : register( SHADER_SPECIFIC_CONST_4 );
const float4 g_EP5 : register( SHADER_SPECIFIC_CONST_5 );
const float4 g_EP6 : register( SHADER_SPECIFIC_CONST_6 );
const float4 g_EP7 : register( SHADER_SPECIFIC_CONST_7 );
const float4 g_EP8 : register( SHADER_SPECIFIC_CONST_8 );
const float4 g_EP9 : register( SHADER_SPECIFIC_CONST_9 );

struct VS_INPUT {
    float4 vPos : POSITION;
    float2 vBaseTexCoord : TEXCOORD0;
    float4 vBoneWeights : BLENDWEIGHT;
    float4 vBoneIndices : BLENDINDICES;
    float3 vPosFlex : POSITION1;
};
struct VS_OUTPUT {
    float4 vProjPos : POSITION;
    float2 vBaseTexCoord : TEXCOORD0;
    float3 vWoundData : TEXCOORD1;
};

#define WOUND_RANGE_CENTER 500.0
#define WOUND_RANGE_ANGLE 6.2831853
#define WOUND_RANGE_RADIUS 100.0

void Unpack2(float packed, out float a, out float b) { float k=floor(packed); b=k/2048.0; a=packed-k; }
float DenormCenter(float v) { return v*(2.0*WOUND_RANGE_CENTER)-WOUND_RANGE_CENTER; }
float DenormAngle(float v) { return v*WOUND_RANGE_ANGLE; }
float DenormRadius(float v) { return v*WOUND_RANGE_RADIUS; }

void DecodeEllipsoid(float f0,float f1,float f2,float f3,float f4,out float3 c,out float3 e,out float3 r)
{
    float a,b;
    Unpack2(f0,a,b); c=float3(DenormCenter(a),DenormCenter(b),0);
    Unpack2(f1,a,b); c.z=DenormCenter(a); e=float3(DenormAngle(b),0,0);
    Unpack2(f2,a,b); e.y=DenormAngle(a); e.z=DenormAngle(b);
    Unpack2(f3,a,b); r=float3(DenormRadius(a),DenormRadius(b),DenormRadius(f4));
}
float3 EllipsoidLocal(float3 p,float3 c,float3 e,float3 r)
{
    float sp=sin(e.x),cp=cos(e.x),sy=sin(e.y),cy=cos(e.y),sr=sin(e.z),cr=cos(e.z);
    float3 col0=float3(cp*cy,cp*sy,-sp);
    float3 col1=float3(sp*sr*cy-cr*sy,sp*sr*sy+cr*cy,sr*cp);
    float3 col2=float3(sp*cr*cy+sr*sy,sp*cr*sy-sr*cy,cr*cp);
    float3 d=p-c;
    return float3(dot(d,col0),dot(d,col1),dot(d,col2))/max(r,float3(1e-4,1e-4,1e-4));
}
float3 EllipsoidWorld(float3 c,float3 e,float3 r,float3 q)
{
    float sp=sin(e.x),cp=cos(e.x),sy=sin(e.y),cy=cos(e.y),sr=sin(e.z),cr=cos(e.z);
    float3 row0=float3(cp*cy,sp*sr*cy-cr*sy,sp*cr*cy+sr*sy);
    float3 row1=float3(cp*sy,sp*sr*sy+cr*cy,sp*cr*sy-sr*cy);
    float3 row2=float3(-sp,sr*cp,cr*cp);
    float3 rq=r*q;
    return c+float3(dot(row0,rq),dot(row1,rq),dot(row2,rq));
}
void Consider(float3 p,float f0,float f1,float f2,float f3,float f4,
              inout float3 bestPos,inout float3 bestWd,inout float bestDist)
{
    float3 c,e,r; DecodeEllipsoid(f0,f1,f2,f3,f4,c,e,r);
    float3 q=EllipsoidLocal(p,c,e,r); float d=length(q); float3 wd=float3(q.yz,d);
    q.x=-abs(q.x); float3 qn=q/max(d,1e-6); float3 dp=EllipsoidWorld(c,e,r,qn);
    float use=step(d,bestDist); bestPos=lerp(bestPos,dp,use); bestWd=lerp(bestWd,wd,use); bestDist=min(bestDist,d);
}

VS_OUTPUT main(const VS_INPUT v)
{
    VS_OUTPUT o=(VS_OUTPUT)0; float3 p=v.vPos.xyz;
    float3 bestPos=p,bestWd=float3(0,0,1e6); float bestDist=1e20;
    Consider(p,g_EP0.x,g_EP0.y,g_EP0.z,g_EP0.w,g_EP1.x,bestPos,bestWd,bestDist);
    Consider(p,g_EP1.y,g_EP1.z,g_EP1.w,g_EP2.x,g_EP2.y,bestPos,bestWd,bestDist);
    Consider(p,g_EP2.z,g_EP2.w,g_EP3.x,g_EP3.y,g_EP3.z,bestPos,bestWd,bestDist);
    Consider(p,g_EP3.w,g_EP4.x,g_EP4.y,g_EP4.z,g_EP4.w,bestPos,bestWd,bestDist);
    Consider(p,g_EP5.x,g_EP5.y,g_EP5.z,g_EP5.w,g_EP6.x,bestPos,bestWd,bestDist);
    Consider(p,g_EP6.y,g_EP6.z,g_EP6.w,g_EP7.x,g_EP7.y,bestPos,bestWd,bestDist);
    Consider(p,g_EP7.z,g_EP7.w,g_EP8.x,g_EP8.y,g_EP8.z,bestPos,bestWd,bestDist);
    Consider(p,g_EP8.w,g_EP9.x,g_EP9.y,g_EP9.z,g_EP9.w,bestPos,bestWd,bestDist);
    float3 finalPos=lerp(p,bestPos,step(bestDist,1.0));
    ApplyMorph(v.vPosFlex,finalPos);
    float3 worldPos; SkinPosition(g_bSkinning,float4(finalPos,1),v.vBoneWeights,v.vBoneIndices,worldPos);
    o.vProjPos=mul(float4(worldPos,1),cViewProj); o.vBaseTexCoord=v.vBaseTexCoord; o.vWoundData=bestWd; return o;
}
'''

VD_PS = r'''#include "common_ps_fxc.h"
#define WOUND_DEFORM_SIZE 1.0
sampler BaseTextureSampler : register(s0);
sampler DeformedTextureSampler : register(s1);
sampler ProjTextureSampler : register(s2);
const float g_BloodRange : register(c0);
struct PS_INPUT { float2 vBaseTexCoord:TEXCOORD0; float3 vWoundData:TEXCOORD1; };
float4 main(PS_INPUT i):COLOR
{
    float4 baseColor=tex2D(BaseTextureSampler,i.vBaseTexCoord);
    float4 projColor=tex2D(ProjTextureSampler,i.vWoundData.xy);
    float weight=1-smoothstep(1.0,1.0+g_BloodRange,i.vWoundData.z);
    baseColor.rgb=lerp(baseColor.rgb,projColor.rgb,saturate(weight));
    float deform=step(i.vWoundData.z,WOUND_DEFORM_SIZE);
    float4 deformed=tex2D(DeformedTextureSampler,i.vBaseTexCoord);
    return lerp(baseColor,deformed,deform);
}
'''
write('binary/src/shaders/hlsl/VertexDeformation_vs30.hlsl', VD_VS)
write('binary/src/shaders/hlsl/VertexDeformation_ps30.hlsl', VD_PS)

rel='binary/src/shaders/hlsl/VertexDeformationVertexLit_vs30.hlsl'
s=read(rel)
old='''const float4 g_EP0 : register( SHADER_SPECIFIC_CONST_4 );\nconst float4 g_EP1 : register( SHADER_SPECIFIC_CONST_5 );\nconst float4 g_EP2 : register( SHADER_SPECIFIC_CONST_6 );\nconst float4 g_EP3 : register( SHADER_SPECIFIC_CONST_7 );'''
new=old+'''\nconst float4 g_EP4 : register( SHADER_SPECIFIC_CONST_8 );\nconst float4 g_EP5 : register( SHADER_SPECIFIC_CONST_9 );\nconst float4 g_EP6 : register( SHADER_SPECIFIC_CONST_10 );\nconst float4 g_EP7 : register( SHADER_SPECIFIC_CONST_11 );\nconst float4 g_EP8 : register( SHADER_SPECIFIC_CONST_12 );\nconst float4 g_EP9 : register( SHADER_SPECIFIC_CONST_13 );'''
s=replace_once(s,old,new,'VDVL VS constants')
s=sub_once(s,
 r'\tfloat4 woundData01\s*:\s*TEXCOORD5;\n\tfloat4 woundData2\s*:\s*TEXCOORD6;\n\tfloat4 woundTail\s*:\s*TEXCOORD7;',
 '\tfloat3 woundData\t\t: TEXCOORD5;\n\tfloat4 woundTail\t\t: TEXCOORD6;', 'VDVL VS output')
insert = r'''
void DecodeEllipsoid8(float f0,float f1,float f2,float f3,float f4,out float3 c,out float3 e,out float3 r)
{
    float a,b;
    Unpack2(f0,a,b); c=float3(DenormCenter(a),DenormCenter(b),0);
    Unpack2(f1,a,b); c.z=DenormCenter(a); e=float3(DenormAngle(b),0,0);
    Unpack2(f2,a,b); e.y=DenormAngle(a); e.z=DenormAngle(b);
    Unpack2(f3,a,b); r=float3(DenormRadius(a),DenormRadius(b),DenormRadius(f4));
}
void ConsiderEllipsoid8(float3 p,float f0,float f1,float f2,float f3,float f4,
    inout float3 bestPos,inout float3 bestWd,inout float3 bestNormal,inout float bestDist)
{
    float3 c,e,r; DecodeEllipsoid8(f0,f1,f2,f3,f4,c,e,r);
    float3 wd,dn; float d;
    float3 dp=ProcessEllipsoid(p,c,e,r,wd,d,dn);
    float use=step(d,bestDist);
    bestPos=lerp(bestPos,dp,use); bestWd=lerp(bestWd,wd,use);
    bestNormal=lerp(bestNormal,dn,use); bestDist=min(bestDist,d);
}

'''
s=replace_once(s,'VS_OUTPUT main( const VS_INPUT v )',insert+'VS_OUTPUT main( const VS_INPUT v )','VDVL VS helper')
pattern=r'\tfloat f0 = g_EP0\.x,.*?\tfloat3 finalModelNormal = normalize\(\n\t\tlerp\( vNormal, selectedDnormal, deformFactor \)\n\t\);'
repl=r'''\tfloat3 selectedDpos = modelPos;
\tfloat3 selectedWd = float3(0.0f, 0.0f, 1e6f);
\tfloat3 selectedDnormal = vNormal;
\tfloat bestDist = 1e20f;
\tConsiderEllipsoid8(modelPos,g_EP0.x,g_EP0.y,g_EP0.z,g_EP0.w,g_EP1.x,selectedDpos,selectedWd,selectedDnormal,bestDist);
\tConsiderEllipsoid8(modelPos,g_EP1.y,g_EP1.z,g_EP1.w,g_EP2.x,g_EP2.y,selectedDpos,selectedWd,selectedDnormal,bestDist);
\tConsiderEllipsoid8(modelPos,g_EP2.z,g_EP2.w,g_EP3.x,g_EP3.y,g_EP3.z,selectedDpos,selectedWd,selectedDnormal,bestDist);
\tConsiderEllipsoid8(modelPos,g_EP3.w,g_EP4.x,g_EP4.y,g_EP4.z,g_EP4.w,selectedDpos,selectedWd,selectedDnormal,bestDist);
\tConsiderEllipsoid8(modelPos,g_EP5.x,g_EP5.y,g_EP5.z,g_EP5.w,g_EP6.x,selectedDpos,selectedWd,selectedDnormal,bestDist);
\tConsiderEllipsoid8(modelPos,g_EP6.y,g_EP6.z,g_EP6.w,g_EP7.x,g_EP7.y,selectedDpos,selectedWd,selectedDnormal,bestDist);
\tConsiderEllipsoid8(modelPos,g_EP7.z,g_EP7.w,g_EP8.x,g_EP8.y,g_EP8.z,selectedDpos,selectedWd,selectedDnormal,bestDist);
\tConsiderEllipsoid8(modelPos,g_EP8.w,g_EP9.x,g_EP9.y,g_EP9.z,g_EP9.w,selectedDpos,selectedWd,selectedDnormal,bestDist);
\tfloat deformFactor = step(bestDist, 1.0f);
\tfloat3 finalModelPos = lerp(modelPos, selectedDpos, deformFactor);
\tfloat3 finalModelNormal = normalize(lerp(vNormal, selectedDnormal, deformFactor));'''
s=sub_once(s,pattern,repl,'VDVL VS wound core')
s=sub_once(s,
 r'\to\.woundData01 = float4\( wd0\.xy, wd1\.xy \);\n\to\.woundData2 = float4\( wd2\.xy, wd0\.z, wd1\.z \);\n\to\.woundTail = float4\( wd2\.z, bumpTexCoord\.x, bumpTexCoord\.y, vProjPos\.z \);',
 '\to.woundData = selectedWd;\n\to.woundTail = float4(bumpTexCoord.x, bumpTexCoord.y, vProjPos.z, 0.0f);', 'VDVL VS tail')
write(rel,s)

rel='binary/src/shaders/hlsl/VertexDeformationVertexLit_ps30.hlsl'
s=read(rel)
s=sub_once(s,
 r'\tfloat4 woundData01\s*:\s*TEXCOORD5;\n\tfloat4 woundData2\s*:\s*TEXCOORD6;\n\tfloat4 woundTail\s*:\s*TEXCOORD7;',
 '\tfloat3 woundData\t\t: TEXCOORD5;\n\tfloat4 woundTail\t\t: TEXCOORD6;', 'VDVL PS input')
pattern=r'\tfloat3 woundData0 = .*?\tfloat3 woundAlbedo = lerp\( baseAlbedo, projColor, totalW \);\n\tfloat deformFactor = max\( max\( d0, d1 \), d2 \);'
repl=r'''\tfloat2 bumpTexCoord = i.woundTail.xy;
\tfloat3 rgb0;
\tfloat w0;
\tfloat d0;
\tAccumProjected(i.woundData, rgb0, w0, d0);
\tfloat totalW = saturate(w0);
\tfloat3 projColor = rgb0 / max(totalW, 1e-6);
\tfloat3 baseAlbedo = baseColor.rgb * g_DiffuseModulation.rgb;
\tfloat3 woundAlbedo = lerp(baseAlbedo, projColor, totalW);
\tfloat deformFactor = d0;'''
s=sub_once(s,pattern,repl,'VDVL PS wound block')
s=s.replace('i.woundTail.w','i.woundTail.z')
write(rel,s)

print('\nSW2 EXT8 source patch applied successfully.')
print('Next: rebuild .vcs/.inc with binary/buildshaders30.py, then build x86_x64 Release DLL.')
