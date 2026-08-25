# SEMASCRIPT_REFERENCE_CORPUS_STARTER_v0.1

## Статус
Grammar-expanded starter corpus

## Новые важные кейсы

### Multi-scene invariant scope
Status: `core-pass`
**Human**
```text
inv:zsum(A -> B : resource; B -> C : credit)
```
**Core**
```text
[FRM:INV <law=ZSUM; scp=[[PRC:TRF <src=[ENT:A]; dst=[ENT:B]; obj=[ENT:RESOURCE]>]; [PRC:TRF <src=[ENT:B]; dst=[ENT:C]; obj=[ENT:CREDIT]>]]>]
```

### Multi-scene temporal scope
Status: `core-pass`
**Human**
```text
time:cyc(system change; reserve change)
```
**Core**
```text
[FRM:TIME <mode=CYC; scp=[[PRC:CHG <obj=[ENT:SYSTEM]>]; [PRC:CHG <obj=[ENT:RESERVE]>]]>]
```

### Causal shorthand
Status: `core-pass`
**Human**
```text
time:lin(resource declines => system becomes unstable)
```
**Core**
```text
[FRM:TIME <mode=LIN; scp=[REL:CAU <cau=[STA:DEC <ctx=[ENT:RESOURCE]>]; res=[STA:STB {NEG} <ctx=[ENT:SYSTEM]>]>]>]
```

### Pattern + equality shorthand
Status: `core-pass`, `core-only`
**Human**
```text
pal(A equals A)
```
**Core**
```text
[PAT:PAL <axis=[IDX:CENTER]; scope=[REL:EQU <left=[ENT:A]; right=[ENT:A]>]>]
```

## Итог
Starter corpus теперь уже покрывает не только базовые одиночные формы, но и:
- multi-scene scope;
- richer Human normalization;
- list-scope grammar;
- causal shorthand.
