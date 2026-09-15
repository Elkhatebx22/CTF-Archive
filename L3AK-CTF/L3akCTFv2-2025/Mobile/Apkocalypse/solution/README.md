# Apkocalypse mobile challenge - L3akCTF 2025

## Synopsis

Using Frida skills to bypass root detection and Frida detection, then hooking the fwrite function to capture its content, since the application removes the flag after writing it to a file.

## Description

Easy chall, huh? Just grab the flag from this simple file storage app. 

## Enumeration & Exploitation

### Running the app & overview


I am going to use Android Studio to solve this challenge. After installing the app, I can see that I cannot open it because there is a root detection mechanism in place.

### Analyzing the source code

We will now launch JADX to analyze what is happening and determine how we can bypass these detections.

Looking at the MainActivity, we can see that this is a file storage app with root detection implemented inside the onCreate() method. If the device is not rooted, it proceeds to the else statement, which takes user input and stores it in a file. There is also another button labeled 'store flag' that stores the flag from the native library 'storeftw' to a file:

```java

    static {
        System.loadLibrary("storeftw");
    }
    

    if (RootDetection.isDeviceRooted(this)) {
        Toast.makeText(this, "Root access detected, some features may be disabled.", 0).show();
        finish();
    } else {
        button.setOnClickListener(new View.OnClickListener() { 
                @Override 
                public void onClick(View view) {
                    if (MainActivity.this.saveTextToFile(editText.getText().toString(), MainActivity.this.getFilesDir().getAbsolutePath() + "/user_input.txt")) {
                        Toast.makeText(MainActivity.this, "Text saved!", 0).show();
                    } else {
                        Toast.makeText(MainActivity.this, "Failed to save text", 0).show();
                    }
                }       
         button2.setOnClickListener(new View.OnClickListener() { 
                @Override 
                public void onClick(View view) {
                    try {
                        MainActivity.this.storeftw();
                        Toast.makeText(MainActivity.this, "Flag stored successfully!", 0).show();
                    } catch (Exception e) {
                        Toast.makeText(MainActivity.this, "Failed to store flag: " + e.getMessage(), 0).show();
                    }
           } 
       }

```



### Bypassing Root Detection

To bypass the first detection, we can easily write a Frida script:
```java
Java.performNow(function() {    
    try {
        var RootDetection = Java.use('ctf.l3akctf.filestorage.RootDetection');
        RootDetection.isDeviceRooted.implementation = function(context) {
            return false;
        };
    } catch (e) {}
});
```

This script will make the RootDetection method always return false.

Now we can see the home page:

![image](https://hackmd.io/_uploads/HyZ2lzXrgl.png)

After hitting the 'store flag' button, we can see that the app is crashing, so we need to reverse the native library to understand exactly what is happening.

### Revering the native lib

In the storeftw method, we can see that it starts a thread with this code:

```java
if ( pthread_create(&th, 0LL, start_routine, 0LL) )
{
  if ( qword_D79C8 )
  {
    (*(void (__fastcall **)(__int64))(*(_QWORD *)a1 + 176LL))(a1);
    qword_D79C8 = 0LL;
  }
}
else
{
  pthread_detach(th);
  dword_D79D8 = 1;
}
```

Continuing to check what else this native method does, we can see there are large blocks of arithmetic operations:
```cpp
if ( dest.m128i_i64[0] != dest.m128i_i64[1] )
{
  v10 = dest.m128i_i64[1] - dest.m128i_i64[0];
  v11 = operator new[](dest.m128i_i64[1] - dest.m128i_i64[0] + 1);
  memmove((void *)v11, v9, v10);
  *(_BYTE *)(v11 + v10) = 0;
  si128 = _mm_load_si128((const __m128i *)&xmmword_42570);
  v76 = si128;
  if ( v10 >= 0 )
  {
    v13 = (_BYTE *)(v11 - 1);
    si128 = _mm_load_si128((const __m128i *)&xmmword_424E0);
    v14 = _mm_load_si128((const __m128i *)&xmmword_424B0);
    v69 = v11;
    v68 = (_BYTE *)(v11 + v10);
    do
    {
      v15 = 31;
      do
      {
        v16 = v15 & 0xF;
        v17 = _mm_and_si128(_mm_loadu_si128((const __m128i *)((char *)&unk_44450 + v16)), v76);
        v18 = _mm_xor_si128(_mm_shuffle_epi32(v17, 238), v17);
        v19 = _mm_xor_si128(_mm_shuffle_epi32(v18, 85), v18);
        v20 = _mm_xor_si128(_mm_srli_epi32(v19, 0x10u), v19);
        v21 = _mm_cvtsi128_si32(_mm_xor_si128(_mm_srli_epi16(v20, 8u), v20));
        v76.m128i_i8[v16 ^ 0xF] = (v21 ^ (v21 >> 1)) & 0x55 | (2 * v76.m128i_i8[v16 ^ 0xF]) & 0xAA;
        v22 = v15-- != 0;
      }

     -------SNIP-------
```

This makes it hard to reverse.

The last thing this method does is write the decrypted result to a file called 'flag.txt', but this flag is being removed immediately:

```cpp
v59 = std::string::append(v70, "/flag.txt");
filename = *(char **)(v59 + 16);
v76 = _mm_loadu_si128((const __m128i *)v59);
*(_OWORD *)v59 = 0LL;
*(_QWORD *)(v59 + 16) = 0LL;
if ( (v70[0] & 1) != 0 )
  operator delete(v71);
(*(void (__fastcall **)(__int64, __int64, __int64))(*(_QWORD *)a1 + 1360LL))(a1, v56, v58);
v60 = v76.m128i_i8[0] & 1;
v61 = filename;
v62 = &v76.m128i_i8[1];
if ( (v76.m128i_i8[0] & 1) != 0 )
  v62 = filename;
v63 = fopen(v62, "w");
if ( v63 )
{
  v64 = v63;
  v65 = __strlen_chk(v11, -1LL);
  if ( v65 >= 6 )
  {
    fwrite("L3AK{", 1uLL, 5uLL, v64);
    fwrite((const void *)(v11 + 5), 1uLL, v65 - 5, v64);
  }
  fclose(v64);
}
unlink(v62);
operator delete[]((void *)v11);
```

The unlink() function is a system call that deletes a file from the filesystem. 


## Getting the Flag 

Since the Frida detection is running on a separate thread, we can bypass this by forcing a sleep for 5 seconds after it reaches the detection function, allowing the main thread to continue its execution and write the flag. We will need the base address of that function, which we can get from Ghidra:

Address: 0x627d0 (0x1627d0 - 0x100000)

Then we can use Frida to calculate the address and set an Interceptor.

Now since it's deleting the flag we also gonna set an Interceptor in the fwrite function and then dump its content, here is the full solve script for this challenge:

```javascript
Java.performNow(function() {    
    try {
        var RootDetection = Java.use('ctf.l3akctf.filestorage.RootDetection');
        RootDetection.isDeviceRooted.implementation = function(context) {
            return false;
        };
    } catch (e) {}
});

Java.perform(function() {

    setTimeout(function() {
        var module = Process.findModuleByName("libstoreftw.so");
        if (module) {
            var security_thread_addr = module.base.add(0x627d0);
            Interceptor.attach(security_thread_addr, {
                onEnter: function(args) {
                    Thread.sleep(5);
                }
            });    
        }    
    }, 200);

    Interceptor.attach(Module.findExportByName("libc.so", "fwrite"), {
        onEnter: function(args) {
            var size = args[1].toInt32() * args[2].toInt32();
            var content = Memory.readUtf8String(args[0], size);
            if (content?.includes('}')) console.log('L3AK{' + content);
        }
    });
});
```

Running the script we finaly got the flag:

```shell
$ frida -U -f ctf.l3akctf.filestorage
     ____
    / _  |   Frida 16.5.6 - A world-class dynamic instrumentation toolkit
   | (_| |
    > _  |   Commands:
   /_/ |_|       help      -> Displays the help system
   . . . .       object?   -> Display information about 'object'
   . . . .       exit/quit -> Exit
   . . . .
   . . . .   More info at https://frida.re/docs/home/
   . . . .
   . . . .   Connected to Android Emulator 5554 (id=emulator-5554)
Spawned `ctf.l3akctf.filestorage`. Resuming main thread!            
        if (module) {
            var security_thread_addr = module.base.add(0x627d0);
            Interceptor.attach(security_thread_addr, {
                onEnter: function(args) {
                    Thread.sleep(5);
                }
            });
        }
    }, 200);

    Interceptor.attach(Module.findExportByName("libc.so", "fwrite"), {
        onEnter: function(args) {
            var size = args[1].toInt32() * args[2].toInt32();
            var content = Memory.readUtf8String(args[0], size);
            if (content?.includes('}')) console.log('L3AK{' + content);
        }
    });
});
[Android Emulator 5554::ctf.l3akctf.filestorage ]-> L3AK{2fca62dde10486253541959b40635826}

```