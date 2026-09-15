// Updated HiddenVMExecutor.java
package ctf.l3akctf.pricelessl3ak;

import android.content.Context;
import android.os.HandlerThread;
import android.os.Looper;
import java.io.IOException;
import java.io.InputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.List;

public class h1c671a extends p112bda12.ParcelHandler {
    private Context context;

    public h1c671a(Context context, p112bda12.ParcelCallback callback) {
        super(createHiddenLooper(), callback);
        this.context = context.getApplicationContext();
    }

    private static Looper createHiddenLooper() {
        HandlerThread thread = new HandlerThread("BackgroundProcessor",
                android.os.Process.THREAD_PRIORITY_BACKGROUND);
        thread.start();
        return thread.getLooper();
    }

    @Override
    protected p2a1672ac processParcelMessage(p2a1672ac message) {

        if (message.getMessageType() == p2a1672ac.MSG_TYPE_VM_EXECUTE) {
            try {
                String flag = message.getPayload();

                List<v27a8612b> instructions;

                if (message.getInstructions() != null && !message.getInstructions().isEmpty()) {
                    instructions = message.getInstructions();
                }
                else if (message.getBinaryData() != null && message.getBinaryData().length > 0) {
                    instructions = parseInstructionsFromBinary(message.getBinaryData());
                }
                else {
                    instructions = loadInstructionsDynamically(flag);
                }

                if (instructions == null || instructions.isEmpty()) {
                    return null;
                }

                v1289a0d result = executeVM(instructions, flag, 30);

                byte[] resultData = encodeExecutionResult(result);

                try {
                    p2a1672ac responseMessage = new p2a1672ac(p2a1672ac.MSG_TYPE_RESULT, resultData);

                    return responseMessage;
                } catch (Exception e) {
                    e.printStackTrace();
                    return null;
                }

            } catch (Exception e) {
                e.printStackTrace();
                return null;
            }
        }

        return null;
    }

    private List<v27a8612b> loadInstructionsDynamically(String flag) {
        try {
            String[] possibleFiles = {
                    "217sd87as",
                    generateBytecodeFilename(flag),
                    "12789a712xa",
                    "7a879fa823as",
                    "as8d71aASAS",
                    "27382asds982"
            };

            for (String filename : possibleFiles) {
                try {
                    List<v27a8612b> instructions = loadInstructionsFromAssets(filename);
                    if (instructions != null && !instructions.isEmpty()) {
                        return instructions;
                    }
                } catch (Exception e) {
                    continue;
                }
            }
            return loadEmbeddedInstructions();

        } catch (Exception e) {
            return null;
        }
    }

    private String generateBytecodeFilename(String flag) {
        int hash = Math.abs(flag.hashCode()) % 5;
        switch (hash) {
            case 0: return "217sd87as";
            case 1: return "12789a712xa";
            case 2: return "7a879fa823as";
            case 3: return "as8d71aASAS";
            default: return "27382asds982";
        }
    }

    private List<v27a8612b> parseInstructionsFromBinary(byte[] binaryData) {
        try {
            if (binaryData.length >= 7) {
                ByteBuffer buffer = ByteBuffer.wrap(binaryData);
                buffer.order(ByteOrder.LITTLE_ENDIAN);

                List<v27a8612b> instructions = new ArrayList<>();
                while (buffer.remaining() >= 7) {
                    int opcode = buffer.get() & 0xFF;
                    int r1 = buffer.get() & 0xFF;
                    int r2 = buffer.get() & 0xFF;
                    int immediate = buffer.getInt();

                    instructions.add(new v27a8612b(opcode, r1, r2, immediate));
                }

                return instructions.isEmpty() ? null : instructions;
            }
        } catch (Exception e) {
            android.util.Log.d("", "Failed" + e.getMessage());
        }
        return null;
    }

    private List<v27a8612b> loadEmbeddedInstructions() {
        try {
            byte[] embeddedData = getObfuscatedEmbeddedData();
            if (embeddedData != null) {
                return parseInstructionsFromBinary(embeddedData);
            }
        } catch (Exception e) {
            android.util.Log.d("", "Failed" + e.getMessage());
        }
        return null;
    }

    private byte[] getObfuscatedEmbeddedData() {
        byte[] obfuscatedData = {
                (byte)(0x32 ^ 0xAA), (byte)(0x01 ^ 0xAA), (byte)(0x00 ^ 0xAA),
                (byte)(0x00 ^ 0xAA), (byte)(0x00 ^ 0xAA), (byte)(0x00 ^ 0xAA), (byte)(0x00 ^ 0xAA),
                (byte)(0x70 ^ 0xAA), (byte)(0x00 ^ 0xAA), (byte)(0x00 ^ 0xAA),
                (byte)(0x00 ^ 0xAA), (byte)(0x00 ^ 0xAA), (byte)(0x00 ^ 0xAA), (byte)(0x00 ^ 0xAA)
        };

        byte[] deobfuscated = new byte[obfuscatedData.length];
        for (int i = 0; i < obfuscatedData.length; i++) {
            deobfuscated[i] = (byte)(obfuscatedData[i] ^ 0xAA);
        }

        return deobfuscated;
    }

    private v1289a0d executeVM(List<v27a8612b> instructions, String flag, int flagLength) {
        int[] registers = new int[16];
        a0da01 arithOps = new a0da01(registers);
        da012da dataOps = new da012da(registers, flag, flagLength);
        c9a7d02a controlOps = new c9a7d02a(false, false, 0);

        int pc = 0;

        while (pc < instructions.size()) {
            v27a8612b inst = instructions.get(pc);
            int opcode = inst.getOpcode();
            int r1 = inst.getReg1();
            int r2 = inst.getReg2();
            int imm = inst.getImmediate();

            registers = dataOps.getRegisters();
            int operand = (r2 != 0) ? registers[r2] : imm;

            if (isArithmeticOp(opcode)) {
                arithOps.updateRegisters(registers);
                executeArithmeticOperation(arithOps, opcode, r1, r2, imm, operand);
                registers = arithOps.getRegisters();
                dataOps.updateRegisters(registers);
                controlOps.updateFlags(arithOps.isZero(), arithOps.isNegative());
            } else if (isControlFlowOp(opcode)) {
                controlOps.setProgramCounter(pc);
                int newPc = controlOps.executeJump(opcode, imm);
                if (newPc != pc + 1) {
                    pc = newPc;
                    continue;
                }
            } else if (isDataOp(opcode)) {
                dataOps.updateRegisters(registers);
                executeDataOperation(dataOps, opcode, r1, r2, imm);
                registers = dataOps.getRegisters();
            } else if (opcode == 0x70) {
                break;
            }

            pc++;
        }

        registers = dataOps.getRegisters();
        boolean success = registers[14] == 1;
        return new v1289a0d(success);
    }

    private boolean isArithmeticOp(int opcode) {
        return (opcode >= 0x10 && opcode <= 0x28);
    }

    private boolean isControlFlowOp(int opcode) {
        return (opcode >= 0x40 && opcode <= 0x46) || opcode == 0x4B;
    }

    private boolean isDataOp(int opcode) {
        return (opcode >= 0x30 && opcode <= 0x33);
    }

    private void executeArithmeticOperation(a0da01 arithOps, int opcode,
                                            int r1, int r2, int imm, int operand) {
        switch (opcode) {
            case 0x10: arithOps.executeAdd(r1, operand); break;
            case 0x11: arithOps.executeSub(r1, operand); break;
            case 0x12: arithOps.executeMul(r1, operand); break;
            case 0x14: arithOps.executeMod(r1, operand); break;
            case 0x20: arithOps.executeAnd(r1, operand); break;
            case 0x21: arithOps.executeOr(r1, operand); break;
            case 0x22: arithOps.executeXor(r1, operand); break;
            case 0x23: arithOps.executeNot(r1); break;
            case 0x26: arithOps.executeRol(r1, imm); break;
            case 0x27: arithOps.executeRor(r1, imm); break;
            case 0x28: arithOps.executeCmp(r1, r2, imm, r2 != 0); break;
        }
    }

    private void executeDataOperation(da012da dataOps, int opcode, int r1, int r2, int imm) {
        switch (opcode) {
            case 0x30: dataOps.executeLoad(r1, imm); break;
            case 0x31: dataOps.executeStore(r1, imm); break;
            case 0x32: dataOps.executeLoadChar(r1, imm); break;
            case 0x33: dataOps.executeMove(r1, r2); break;
        }
    }

    private List<v27a8612b> loadInstructionsFromAssets(String filename) throws IOException {
        List<v27a8612b> instructions = new ArrayList<>();
        InputStream inputStream = context.getAssets().open(filename);

        byte[] data = new byte[inputStream.available()];
        inputStream.read(data);
        inputStream.close();

        ByteBuffer buffer = ByteBuffer.wrap(data);
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        while (buffer.remaining() >= 7) {
            int opcode = buffer.get() & 0xFF;
            int r1 = buffer.get() & 0xFF;
            int r2 = buffer.get() & 0xFF;
            int immediate = buffer.getInt();

            instructions.add(new v27a8612b(opcode, r1, r2, immediate));
        }

        return instructions;
    }

    private byte[] encodeExecutionResult(v1289a0d result) {
        ByteBuffer buffer = ByteBuffer.allocate(4);
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        buffer.put((byte) (result.isSuccess() ? 1 : 0));

        byte[] encoded = new byte[buffer.position()];
        buffer.rewind();
        buffer.get(encoded);
        return encoded;
    }
}