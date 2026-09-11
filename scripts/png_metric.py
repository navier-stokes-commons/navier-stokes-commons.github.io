#!/usr/bin/env python3
"""Tiny stdlib PNG decoder for audit screenshot difference metrics.

Supports non-interlaced 8-bit RGB/RGBA/greyscale PNGs emitted by Chromium.
No production runtime dependency; used only by audit scripts.
"""
from __future__ import annotations
import struct,zlib

_SIG=b'\x89PNG\r\n\x1a\n'

def _paeth(a:int,b:int,c:int)->int:
    p=a+b-c; pa=abs(p-a); pb=abs(p-b); pc=abs(p-c)
    return a if pa<=pb and pa<=pc else (b if pb<=pc else c)

def decode_rgb(data:bytes)->tuple[int,int,bytes]:
    if not data.startswith(_SIG): raise ValueError('not PNG')
    pos=len(_SIG); w=h=depth=ctype=interlace=None; compressed=bytearray()
    while pos<len(data):
        if pos+8>len(data): raise ValueError('truncated PNG')
        n=struct.unpack('>I',data[pos:pos+4])[0]; typ=data[pos+4:pos+8]; pos+=8
        payload=data[pos:pos+n]; pos+=n+4  # skip CRC
        if typ==b'IHDR':
            w,h,depth,ctype,comp,filt,interlace=struct.unpack('>IIBBBBB',payload)
            if comp!=0 or filt!=0: raise ValueError('unsupported PNG method')
        elif typ==b'IDAT': compressed.extend(payload)
        elif typ==b'IEND': break
    if not w or not h or depth!=8 or interlace!=0: raise ValueError(f'unsupported PNG geometry/depth/interlace {w}x{h} depth={depth} interlace={interlace}')
    channels={0:1,2:3,6:4}.get(ctype)
    if channels is None: raise ValueError(f'unsupported PNG color type {ctype}')
    raw=zlib.decompress(bytes(compressed)); stride=w*channels; expected=h*(stride+1)
    if len(raw)!=expected: raise ValueError(f'PNG decompressed length {len(raw)} != {expected}')
    rows=[]; prior=bytearray(stride); off=0
    for _ in range(h):
        f=raw[off]; off+=1; scan=bytearray(raw[off:off+stride]); off+=stride
        for i,x in enumerate(scan):
            a=scan[i-channels] if i>=channels else 0; b=prior[i]; c=prior[i-channels] if i>=channels else 0
            if f==1: scan[i]=(x+a)&255
            elif f==2: scan[i]=(x+b)&255
            elif f==3: scan[i]=(x+((a+b)//2))&255
            elif f==4: scan[i]=(x+_paeth(a,b,c))&255
            elif f!=0: raise ValueError(f'unsupported PNG filter {f}')
        rows.append(scan); prior=scan
    out=bytearray(w*h*3); j=0
    for row in rows:
        if ctype==0:
            for v in row: out[j:j+3]=bytes((v,v,v)); j+=3
        else:
            for i in range(0,len(row),channels): out[j:j+3]=row[i:i+3]; j+=3
    return w,h,bytes(out)

def mad_png(a:bytes,b:bytes)->float:
    wa,ha,pa=decode_rgb(a); wb,hb,pb=decode_rgb(b)
    if (wa,ha)!=(wb,hb): raise ValueError(f'PNG geometry mismatch {(wa,ha)} vs {(wb,hb)}')
    return sum(abs(x-y) for x,y in zip(pa,pb))/(len(pa)*255.0)
