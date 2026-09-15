# PricelessL3ak mobile challenge - L3akCTF 2025  


## Synopsis

This challenge involves identifying a lifecycle intent vulnerability. The flags from the lifecycle intent serve as the decryption key for a file containing VM instructions. These instructions are executed in the background using IPC parcel communication.
<br>
## Description

Basic flag checker app, or is it?
<br>
## Enumeration & Exploitation

### Running the app & overview

First, we'll use Android Studio to examine the challenge and understand its functionality. We can see that it's simply a flag checker - when we input any text, it displays an "Wrong" message. 
<br>
### Analyzing the source code

+ When examining the challenge, we're provided with an Android APK that can be decompiled using tools like JADX. The code appears to be obfuscated with ProGuard, as evidenced by the shortened class names and restructured packages.

Looking at the MainActivity, we can see that it takes user input, calculates the SHA256 hash of that input, and compares it with a hardcoded hash. Strange, right?

```java
    private void checkFlag(String str) {
        String calculateSHA256 = calculateSHA256(str);
        if (calculateSHA256 == null || !calculateSHA256.equals(TARGET_HASH)) {
            this.resultText.setText("Wrong!");
            this.resultText.setTextColor(getColor(R.color.holo_red_dark));
        } else {
            this.resultText.setText("Correct!");
            this.resultText.setTextColor(getColor(R.color.holo_green_dark));
        }
    }
```

Let's go back and analyze the AndroidManifest.xml file to check for any exported components:

```java
<activity
 android:theme="@android:style/Theme.Translucent.NoTitleBar"
 android:name="ctf.l3akctf.pricelessl3ak.h1832fla12"
 android:exported="true"/>
```

From this, we can see there's an exported activity. Let's navigate to that class and examine its functionality.

```java
public class h1832fla12 extends Activity {

    public static final 
    int f1490b = 0;
    public h f1491a;
    
    @Override 
    public final void onCreate(Bundle bundle) {
        super.onCreate(bundle);
        h hVar = new h();
        hVar.f360a = this;
        c cVar = new c();
        cVar.f5a = this;
        hVar.f361b = cVar;
        this.f1491a = hVar;
        if (!"BINGO".equals(getIntent().getAction())) {
            finish();
            return;
        }
        h hVar2 = this.f1491a;
        h1832fla12 h1832fla12Var = (h1832fla12) hVar2.f360a;
        try {
            InputStream open = h1832fla12Var.getAssets().open("data.enc");
            byte[] bArr = new byte[open.available()];
            hVar2.f362c = bArr;
            open.read(bArr);
            open.close();
        } catch (Exception unused) {
            h1832fla12Var.finish();
        }
    }

    @Override 
    public final void onNewIntent(Intent intent) {
        String stringExtra;
        super.onNewIntent(intent);
        setIntent(intent);
        if ("BANGO".equals(intent.getAction())) {
            h hVar = this.f1491a;
            if (((byte[]) hVar.f362c) == null || intent.getFlags() == 0 || (stringExtra = intent.getStringExtra("f")) == null) {
                return;
            }
            int flags = intent.getFlags();
            byte[] bArr = (byte[]) hVar.f362c;
            C0003d c0003d = new C0003d(9, hVar);
            c cVar = (c) hVar.f361b;
            cVar.getClass();
            try {
                cVar.h(c0003d, stringExtra, c.j(c.g(bArr, flags)));
            } catch (Exception e2) {
                c0003d.v(" " + e2.getMessage());
            }
        }
    }
}
```

From this class, we can observe a two-stage lifecycle intent vulnerability:

+ Stage 1 (onCreate): The activity receives an intent and checks if the action equals "BINGO". If successful, it loads an encrypted file (data.enc) from the assets into memory, but performs no other operations.

+ Stage 2 (onNewIntent): The activity receives a second intent with action "BANGO" and an extra parameter "f". If the loaded data exists, intent flags are present, and the "f" parameter is not empty, it processes the encrypted data by passing the loaded bytes, intent flags, and the "f" parameter to cVar.h(c0003d, stringExtra, c.j(c.g(bArr, flags))).

This creates a lifecycle intent vulnerability. We'll build our own exploit app to trigger this behavior.
<br>
### Exploiting the lifecycle intent




Here's the code to exploit the lifecycle intent vulnerability:
```java
@Override
    public void onClick(View v) {
        String f = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa";

        Intent openIntent = new Intent();
        openIntent.setComponent(new ComponentName("ctf.l3akctf.pricelessl3ak", "ctf.l3akctf.pricelessl3ak.h1832fla12"));
        openIntent.setAction("BINGO");
        openIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        startActivity(openIntent);

        Intent reopenIntent = new Intent();
        reopenIntent.setComponent(new ComponentName("ctf.l3akctf.pricelessl3ak", "ctf.l3akctf.pricelessl3ak.h1832fla12"));
        reopenIntent.setAction("BANGO");
        reopenIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
        reopenIntent.addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP);
        reopenIntent.putExtra("f", f);

        new Handler().postDelayed(() -> {
            startActivity(reopenIntent);
        }, 1000);
    }
```

after building and running the app, clicking the button successfully exploits the lifecycle intent vulnerability. We receive a popup message indicating "failed," which suggests there's an additional flag validation process occurring. We'll now proceed to decrypt the file and analyze what operations are being performed.

First, the method processes the encrypted data using two parameters: the encrypted data itself and the intent flags. The intent flags we're using are:
```java
reopenIntent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
reopenIntent.addFlags(Intent.FLAG_ACTIVITY_SINGLE_TOP);
```

These flags have the following hex values:

FLAG_ACTIVITY_NEW_TASK → 0x10000000
FLAG_ACTIVITY_SINGLE_TOP → 0x20000000

Since the method doesn't check for a specific flag, the two flags will be combined into a single value with or operation:

FLAG_ACTIVITY_NEW_TASK | FLAG_ACTIVITY_SINGLE_TOP → 0x10000000 | 0x20000000 = 0x30000000

Now we have the key (0x30000000) used for decrypting the file. Here's the decryption algorithm:

```java
private static final long SEED = 0x30000000L;

public static byte[] decrypt(byte[] data) {
    byte[] result = data.clone();

    for (int i = result.length - 1; i >= 1; i--) {
        result[i] ^= result[i-1];
    }

    for (int i = 0; i < result.length; i++) {
        int rotAmount = (i % 7) + 1;
        result[i] = (byte)rotateRight(result[i] & 0xFF, rotAmount);
    }
    
    for (int i = 0; i < result.length; i++) {
        int addValue = (i * 0x13 + (int)(SEED & 0xFF)) & 0xFF;
        result[i] = (byte)((result[i] - addValue) & 0xFF);
    }
    
    for (int i = 0; i < result.length; i++) {
        int keyByte = (int)((SEED >> ((i % 4) * 8)) & 0xFF);
        result[i] ^= keyByte;
    }
    
    return result;
}
```
we now have the decrypted file.
<br>
### IPC Parcel Communication

The next step involves understanding how the decrypted data is processed using Android's Parcel mechanism. The c.j method is responsible for parsing the decrypted bytes into a structured format:

```java
public static ArrayList j(byte[] bArr) {
    ArrayList arrayList = new ArrayList();
    ByteBuffer wrap = ByteBuffer.wrap(bArr);
    wrap.order(ByteOrder.LITTLE_ENDIAN);
    while (wrap.remaining() >= 7) {
        arrayList.add(new v27a8612b(wrap.get() & 255, wrap.get() & 255, wrap.get() & 255, wrap.getInt()));
    }
    if (arrayList.isEmpty()) {
        throw new Exception("?");
    }
    return arrayList;
}
```

This method parses the decrypted data by:

1 - Creating a ByteBuffer with little-endian byte order
2 - Reading chunks of 7 bytes at a time (3 bytes + 1 integer = 7 bytes total)
3 - Creating v27a8612b objects from each 7-byte chunk
4 - Returning an ArrayList of these parsed objects

The v27a8612b class is a Parcelable object that stores structured data:

```java
public class v27a8612b implements Parcelable {
    public final int f1498a; 
    public final int f1499b;  
    public final int f1500c; 
    public final int f1501d; 
    

    public v27a8612b(int i2, int i3, int i4, int i5) {
        this.f1498a = i2;
        this.f1499b = i3;
        this.f1500c = i4;
        this.f1501d = i5;
    }
    
    @Override
    public void writeToParcel(Parcel parcel, int i2) {
        parcel.writeInt(this.f1498a);
        parcel.writeInt(this.f1499b);
        parcel.writeInt(this.f1500c);
        parcel.writeInt(this.f1501d);
    }
}

```

the Parcelable implementation allows these objects to be efficiently serialized and passed between Android components via IPC (Inter-Process Communication). Each v27a8612b object represents a structured data element with four integer fields, and the collection of these objects forms the complete parsed dataset from the decrypted file.

The h method acts as an entry point that forwards the processed data to the next stage:
```java
public void h(C0003d c0003d, String str, ArrayList arrayList) {
    try {
        if (((X.c) this.f6b) == null) {
            h1832fla12 h1832fla12Var = (h1832fla12) this.f5a;
            X.c cVar = new X.c();
            cVar.f353c = false;
            cVar.f352b = h1832fla12Var.getApplicationContext();
            this.f6b = cVar;
            cVar.b();
        }
        ((X.c) this.f6b).a(new C0003d(8, c0003d), str, arrayList);
    } catch (Exception e2) {
        c0003d.v("Error: " + e2.getMessage());
    }
}
```

The method first checks if some component (X.c) is already set up. If not, it creates one and configures it with the app context - kind of like making sure you have the right tool for the job before you start working.

Then it takes everything we've gathered so far - our flag input, those parsed bytes objects, and a way to report back what happens - and hands it all off to this X.c component to do.

The X.c class is essentially a communication bridge that handles the transition from our exploited data to whatever processing system comes next:

```java
public final class c {
    public a f351a;
    public Context f352b;
    public boolean f353c;

    public final void a(C0003d c0003d, String str, ArrayList arrayList) {
        if (!this.f353c) {
            b();
        }
        h k2 = h.k();
        p2a1672ac p2a1672acVar = !arrayList.isEmpty() ? new p2a1672ac(str, arrayList) : new p2a1672ac(str, (ArrayList) null);
        b bVar = new b(c0003d);
        ConcurrentHashMap concurrentHashMap = (ConcurrentHashMap) k2.f360a;
        int i2 = p2a1672acVar.f1492a;
        f fVar = (f) concurrentHashMap.get(Integer.valueOf(i2));
        if (fVar == null) {
            bVar.b("No handler registered for message type: " + i2);
            return;
        }
        Parcel obtain = Parcel.obtain();
        p2a1672acVar.writeToParcel(obtain, 0);
        Message obtainMessage = fVar.obtainMessage();
        obtainMessage.obj = obtain;
        int incrementAndGet = ((AtomicInteger) k2.f362c).incrementAndGet();
        obtainMessage.what = incrementAndGet;
        ((ConcurrentHashMap) k2.f361b).put(Integer.valueOf(incrementAndGet), bVar);
        fVar.sendMessageDelayed(obtainMessage, 50L);
    }

    public final void b() {
        if (this.f353c) {
            return;
        }
        h k2 = h.k();
        this.f351a = new a();
        a aVar = this.f351a;
        HandlerThread handlerThread = new HandlerThread("BackgroundProcessor", 10);
        handlerThread.start();
        f fVar = new f(handlerThread.getLooper());
        new WeakReference(aVar);
        fVar.f357a = this.f352b.getApplicationContext();
        ((ConcurrentHashMap) k2.f360a).put(4919, fVar);
        this.f353c = true;
    }
}

```

What this class actually does:

+ Initialization (b method): Sets up a background processing system with a dedicated HandlerThread called "BackgroundProcessor". It registers a handler for message type 4919 in some global registry.
+ Message Processing (a method): Takes our flag string and parsed instruction list, wraps them into a p2a1672ac message object, and sends it through the parcel communication system with a 50ms delay.
+ Handler Lookup: It looks up a registered handler for the message type and forwards the parceled data to it. If no handler exists, it reports an error.

The interesting part is that this creates a background thread specifically for processing our data, and uses Android's Parcel system to serialize and send messages between components. However, we still don't know what the actual handler (the f class) does with our instruction data once it receives it.

Moving to the f class, we can see that JADX failed to decompile the code properly and is showing some garbage comments. Don't worry - we can fix this by enabling the 'Show inconsistent code' option in the preferences.

![image](https://hackmd.io/_uploads/ryUJu6GBex.png)

Now we have a clean code of that class:
![image](https://hackmd.io/_uploads/H1t4_6zrgx.png)

we can see this is actually a vm! Looking at the f class (which is the VM executor), we can finally understand what all that parcel communication was leading up to.

Now let's break down the actual parcel communication classes to understand the complete picture:

**p2a1672ac - The Message Container:**

```java
public class p2a1672ac implements Parcelable {
    public final int f1492a;      // message type 
    public final String f1493b;   // flag
    public final ArrayList f1494c; // vm instruction list (v27a8612b objects)
    public final byte[] f1495d;   // raw binary data
    public final int f1496e;      // flags field
}
```

this is the main envelope that carries our data. It can hold either parsed instructions (f1494c) or raw bytes (f1495d), along with our flag (f1493b).

**v27a8612b - VM Instruction Objects:**
```java
public class v27a8612b implements Parcelable {
    public final int f1498a;  // opcode
    public final int f1499b;  // reg 1 
    public final int f1500c;  // reg 2
    public final int f1501d;  // immediate value 
}
```

these represent individual VM instructions. Each 7-byte chunk from our decrypted file becomes one of these objects.


**v1289a0d - VM Result:**
```java
public class v1289a0d implements Parcelable {
    public final boolean f1497a;  // success/failure result
}
```
simple boolean wrapper for the VM execution result.

**c9a7d02a - Control Flow State:**
```java
public class c9a7d02a implements Parcelable {
    public boolean f1482a;  // zero flag 
    public boolean f1483b;  // negative/carry flag
    public int f1484c;      // PC
}
```
**a0da01 - Arithmetic State:**
```java
public class a0da01 implements Parcelable {
    public int[] f1479a;    // register array (16 registers)
    public boolean f1480b;  // zero flag
    public boolean f1481c;  // negative flag  
}
```
**da012da - VM Data Management State:**
```java
public class da012da implements Parcelable {
    public int[] f1485a;           // register array (16 registers)
    public HashMap f1486b;         // memory map (address -> value)
    public String f1487c;          // flag 
    public ArrayList f1488d;       // store tracking
    public int f1489e;            // flag length
}
```
This class essentially represents the "data processing unit" of the vm - it's what tracks all the memory operations, flag characters, and intermediate results during the complex multi-phase algorithm execution.

**handleMessage:**
```java
@Override
public final void handleMessage(Message message) {
    Object obj = message.obj;
    if (obj instanceof Parcel) {
        Parcel parcel = (Parcel) obj;
        parcel.setDataPosition(0);
        try {
            try {
                p2a1672ac e2 = e(p2a1672ac.CREATOR.createFromParcel(parcel));
                g gVar = (g) ((ConcurrentHashMap) h.k().f361b).get(Integer.valueOf(message.what));
                if (gVar != null && e2 != null) {
                    gVar.a(e2);
                } else if (gVar != null) {
                    gVar.b("Processing returned null result");
                }
            } catch (Exception e3) {
            }
        } finally {
            parcel.recycle();
        }
    }
}
```
+ Takes the incoming Message object and extracts the Parcel from it
+ Uses p2a1672ac.CREATOR.createFromParcel(parcel) to reconstruct our message object from the parceled data
+ Calls method e() which contains the actual VM execution logic we saw earlier
+ Finds the appropriate callback (gVar) using the message ID (message.what)
+ Calls gVar.a(e2) to deliver the VM result back to whoever sent the original request
+ Recycles the parcel and removes the callback from the pending list

This parcel system essentially creates a complete VM execution environment that can be serialized and passed between Android components.

### Reversing the VM

Looking at this VM structure, we can now rewrite our disassembler to properly analyze the bytecode:
```python
OPCODE_MAP = {
    0x30: "LOAD", 0x31: "STORE", 0x32: "LOAD_CHAR", 0x33: "MOVE",
    0x10: "ADD",  0x11: "SUB",   0x12: "MUL",       0x14: "MOD",
    0x20: "AND",  0x21: "OR",    0x22: "XOR",       0x23: "NOT",
    0x26: "ROL",  0x27: "ROR",   0x28: "CMP",
    0x40: "JMP",  0x41: "JZ",    0x42: "JNZ",       0x43: "JL",
    0x44: "JG",   0x45: "JLE",   0x46: "JGE",       0x4B: "NOP",
    0x70: "HALT", 0x71: "PRINT",
}
def load_instructions(path):
    ext = os.path.splitext(path)[1].lower()
    data = open(path,'rb').read()
    insts=[]; off=0
    while off+7 < len(data):
        opc,r1,r2,imm = struct.unpack_from('<BBBI', data, off)
        name = OPCODE_MAP.get(opc)
        if not name: raise ValueError(f"Unknown opcode 0x{opc:02X}")
        insts.append({'op_name':name,'reg1':r1,'reg2':r2,'immediate':imm})
        off += 7
    return insts

def disassemble(insts):
    for idx, inst in enumerate(insts):
        addr = idx
        op = inst['op_name']
        r1 = inst['reg1']
        r2 = inst['reg2']
        imm = inst['immediate']
        if op in ("JMP","JZ","JNZ","JL","JG","JLE","JGE"): 
            operand = str(imm)
        else:
            operand = f"r{r2}" if r2 else str(imm)
        print(f"{addr}: {op} r{r1}, {operand}")
        
insts = load_instructions("data.dec")
disassemble(insts)
```

Analyzing the disassembly, we can see the first phase implements ASCII validation and normalization:

```ass
1: CMP r0, 32
2: JL r0, 7
3: CMP r0, 126
4: JG r0, 7
5: SUB r0, 32
6: JMP r0, 8
7: LOAD r0, 31
8: STORE r0, 4096
9: LOAD_CHAR r0, 1
10: CMP r0, 32
11: JL r0, 16
12: CMP r0, 126
13: JG r0, 16
14: SUB r0, 32
15: JMP r0, 17
16: LOAD r0, 31
17: STORE r0, 4097
18: LOAD_CHAR r0, 2
19: CMP r0, 32
20: JL r0, 25
21: CMP r0, 126
22: JG r0, 25
23: SUB r0, 32
24: JMP r0, 26
25: LOAD r0, 31
26: STORE r0, 4098
...
```

This pattern repeats until address 269, processing all 30 bytes (the flag length). Each character is:

+ Loaded from the flag string
+ Validated to be in the printable ASCII range (0x20-0x7E)
+ Normalized by subtracting 0x20 if valid, or set to 0x1F if invalid
+ Stored at memory addresses 0x1000-0x101D

```python
norm = []
for i, c in enumerate(flag):
    v = ord(c)
    if v < 0x20 or v > 0x7E:
        norm.append(0x1F)  character marker
    else:
        norm.append((v - 0x20) & 0xFF) 
```

The next phase processes each normalized character from addresses 0x1000-0x101D:

```ass
270: LOAD r0, 4096
271: XOR r0, 0
272: XOR r0, 0
273: ROL r0, 1
274: AND r0, 255
275: STORE r0, 4352
276: LOAD r0, 4097
277: XOR r0, 23
278: XOR r0, 1
279: ROL r0, 2
280: AND r0, 255
281: STORE r0, 4353
282: LOAD r0, 4098
283: XOR r0, 46
284: XOR r0, 4
285: ROL r0, 3
286: AND r0, 255
287: STORE r0, 4354
...
```

**Pattern Analysis:**

First XOR: Each character is XORed with (index * 0x17) & 0xFF

Index 0: 0 * 0x17 = 0
Index 1: 1 * 0x17 = 23
Index 2: 2 * 0x17 = 46
Index 3: 3 * 0x17 = 69

Second XOR: Result is XORed with (index * index) & 0xFF

Index 0: 0² = 0
Index 1: 1² = 1
Index 2: 2² = 4
Index 3: 3² = 9

Rotation: Value is rotated left by (index % 8) + 1 bits

Storage at addresses 0x1100-0x111D

This phase can be implemented as:
```python
    r1 = []
    for i, v in enumerate(norm):
        v ^= (i * 0x17) & 0xFF
        v ^= (i * i) & 0xFF
        v = rol8(v, (i % 8) + 1)
        r1.append(v)
```

The final transformation phase implements a complex polynomial algorithm with dynamic rotation based on dependencies:
```ass
450: LOAD r0, 4352     
451: LOAD r1, 4352     
452: LOAD r2, 4352     
453: MOVE r3, r1       
454: MUL r3, r3        
455: AND r3, r3        
456: MOVE r4, 0        
457: ADD r4, r3        
458: AND r4, r4        
459: MOVE r5, 0        
460: MUL r5, r2        
461: AND r5, r5        
462: XOR r4, r5        
463: MOVE r6, r1       
464: ADD r6, r2        
465: MOD r6, 8         
466: CMP r6, 0         
467: JZ r0, 482        
...
482: ROR r4, 0         
483: JMP r0, 498       
484: ROR r4, 1         
485: JMP r0, 498       
...
498: AND r4, r4        
499: STORE r4, 4608    
```

**pattern analysis:**

dependencies: Each position i depends on values at (i*3)%30 and (i*7)%30
Polynomial: (current + dep1²) ⊕ (current * dep2)
Dynamic Rotation: ROR by (dep1 + dep2) % 8 using jump table dispatch
Storage: Results stored at 0x1200-0x121D

Equivalent code:
```python
r2 = []
for i, a in enumerate(r1):
    dep1 = r1[(i * 3) % 30]
    dep2 = r1[(i * 7) % 30]
    part1 = (a + (dep1 * dep1)) & 0xFF
    part2 = (dep2 * a) & 0xFF
    v = part1 ^ part2
    rot = (dep1 + dep2) % 8
    v = ror8(v, rot)
    r2.append(v & 0xFF)
```

finally, the algorithm stores the target ciphertext at addresses 0x4000-0x401D and performs validation:
```ass
1949: STORE r4, 4637
1950: LOAD r12, 216
1951: STORE r12, 16384
1952: LOAD r12, 80
1953: STORE r12, 16385
1954: LOAD r12, 35
1955: STORE r12, 16386
1956: LOAD r12, 22
1957: STORE r12, 16387
1958: LOAD r12, 129
1959: STORE r12, 16388
1960: LOAD r12, 176
1961: STORE r12, 16389
1962: LOAD r12, 231
1963: STORE r12, 16390
1964: LOAD r12, 76
1965: STORE r12, 16391
...
```

validation phase compares computed values (0x1200+) against target values (0x4000+):
```ass
2013: CMP r0, r1
2014: JZ r0, 2016
2015: LOAD r14, 0
2016: LOAD r0, 4609
2017: LOAD r1, 16385
2018: CMP r0, r1
2019: JZ r0, 2021
2020: LOAD r14, 0
2021: LOAD r0, 4610
2022: LOAD r1, 16386
2023: CMP r0, r1
2024: JZ r0, 2026
2025: LOAD r14, 0
2026: LOAD r0, 4611
2027: LOAD r1, 16387
2028: CMP r0, r1
2029: JZ r0, 2031
2030: LOAD r14, 0
2031: LOAD r0, 4612
2032: LOAD r1, 16388
2033: CMP r0, r1
2034: JZ r0, 2036
2035: LOAD r14, 0
2036: LOAD r0, 4613
2037: LOAD r1, 16389
...
```

Any mismatch sets r14 to 0 (failure). If all 30 bytes match, r14 remains 1 (correct flag)

## Getting the Flag

Now we have everything needed to solve the challenge. I wrote a z3 solver, but it's generating around 3000 potential flags. Since we're provided with the correct sha256 hash of the flag, we can use it to get the right flag:

```python
import sys
import hashlib
from z3 import *

def rol8_dyn(x, r):
    expr = None
    for i in range(8):
        branch = RotateLeft(x, i)
        cond = (r == BitVecVal(i, r.size()))
        expr = branch if expr is None else If(cond, branch, expr)
    return expr

def get_flag(ct):
    n = len(ct)
    s = Solver()
    r1 = [BitVec(f"r1_{i}", 8) for i in range(n)]

    for i in range(n):
        a = r1[i]
        dep1 = r1[(i * 3) % n]
        dep2 = r1[(i * 7) % n]
        rot = BitVec(f"rot_{i}", 8)
        s.add(rot == (dep1 + dep2) & BitVecVal(0x07, 8))
        ct_bv = BitVecVal(ct[i], 8)
        temp = rol8_dyn(ct_bv, rot)
        rhs = ((a + (dep1 * dep1)) & BitVecVal(0xFF, 8)) ^ ((dep2 * a) & BitVecVal(0xFF, 8))
        s.add(temp == rhs)

    for i in range(n):
        shift = (i % 8) + 1
        inv_rol = RotateLeft(r1[i], 8 - shift)
        k1 = (i * 0x17) & 0xFF
        k2 = (i * i) & 0xFF
        norm = BitVec(f"norm_{i}", 8)
        s.add(norm == inv_rol ^ BitVecVal(k1, 8) ^ BitVecVal(k2, 8))
        ascii_i = BitVec(f"ascii_{i}", 8)
        s.add(ascii_i == norm + BitVecVal(0x20, 8))
    
    s.add(BitVec("ascii_0", 8) == ord("L"))
    s.add(BitVec("ascii_1", 8) == ord("3"))
    s.add(BitVec("ascii_2", 8) == ord("A"))
    s.add(BitVec("ascii_3", 8) == ord("K"))
    s.add(BitVec("ascii_4", 8) == ord("{"))
    s.add(BitVec(f"ascii_{n-1}", 8) == ord("}"))
    
    while s.check() == sat:
        m = s.model()
        flag = ''.join(chr(m[BitVec(f"ascii_{i}", 8)].as_long()) for i in range(n))
        
        flag_hash = hashlib.sha256(flag.encode()).hexdigest()
        if flag_hash == "f3bdd9f68a198756b96c5cf8207db63a11507e50fb0d29be609ff678ef721935":
            print(f"FLAG: {flag}")
            exit()
        
        block = Or(*[ BitVec(f"ascii_{i}", 8) != BitVecVal(ord(flag[i]), 8) for i in range(n)])
        s.add(block)
    return 

ct = [0xd8, 0x50, 0x23, 0x16, 0x81, 0xb0, 0xe7, 0x4c, 0x9a, 0xb5, 0x4b, 0xd9, 0x2a, 0x98, 0x58, 0x14, 0xea, 0xc6, 0x90, 0x51, 0x20, 0x48, 0x43, 0x72, 0x28, 0x85, 0x4b, 0xad, 0xa5, 0x80]
get_flag(ct)

# Flag: L3AK{P4rc3l_cycl3_1Nt3nt_VM!!}
```

and finally we got the flag.