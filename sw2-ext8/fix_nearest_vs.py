from pathlib import Path
import sys

root = Path(sys.argv[1] if len(sys.argv) > 1 else '.').resolve()

def edit(rel, old, new):
    p = root / rel
    s = p.read_text(encoding='utf-8-sig')
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{rel}: expected one match, found {n}')
    p.write_text(s.replace(old, new, 1), encoding='utf-8', newline='\n')
    print('fixed', rel)

# The original pixel shaders accept three wound interpolators.
# Keep them stock and feed only the nearest of the eight EXT8 wounds into slot 0.
edit(
    'binary/src/shaders/hlsl/VertexDeformation_vs30.hlsl',
    '''struct VS_OUTPUT {
    float4 vProjPos : POSITION;
    float2 vBaseTexCoord : TEXCOORD0;
    float3 vWoundData : TEXCOORD1;
};''',
    '''struct VS_OUTPUT {
    float4 vProjPos : POSITION;
    float2 vBaseTexCoord : TEXCOORD0;
    float3 vWoundData0 : TEXCOORD1;
    float3 vWoundData1 : TEXCOORD2;
    float3 vWoundData2 : TEXCOORD3;
};'''
)
edit(
    'binary/src/shaders/hlsl/VertexDeformation_vs30.hlsl',
    'o.vProjPos=mul(float4(worldPos,1),cViewProj); o.vBaseTexCoord=v.vBaseTexCoord; o.vWoundData=bestWd; return o;',
    'o.vProjPos=mul(float4(worldPos,1),cViewProj); o.vBaseTexCoord=v.vBaseTexCoord; o.vWoundData0=bestWd; o.vWoundData1=float3(0,0,1e6); o.vWoundData2=float3(0,0,1e6); return o;'
)

edit(
    'binary/src/shaders/hlsl/VertexDeformationVertexLit_vs30.hlsl',
    '''	float3 woundData		: TEXCOORD5;
	float4 woundTail		: TEXCOORD6;''',
    '''	float4 woundData01		: TEXCOORD5;
	float4 woundData2		: TEXCOORD6;
	float4 woundTail		: TEXCOORD7;'''
)
edit(
    'binary/src/shaders/hlsl/VertexDeformationVertexLit_vs30.hlsl',
    '''	o.woundData = selectedWd;
	o.woundTail = float4(bumpTexCoord.x, bumpTexCoord.y, vProjPos.z, 0.0f);''',
    '''	o.woundData01 = float4(selectedWd.xy, 0.0f, 0.0f);
	o.woundData2 = float4(0.0f, 0.0f, selectedWd.z, 1e6f);
	o.woundTail = float4(1e6f, bumpTexCoord.x, bumpTexCoord.y, vProjPos.z);'''
)

print('EXT8 nearest-wound compatibility layout applied; stock pixel shaders can be reused.')
