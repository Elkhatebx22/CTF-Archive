package ctf.l3akctf.pricelessl3ak;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.ArrayList;
import java.util.List;

public class e12acd1 {


    private h1832fla12 activity;
    private FlagChecker flagChecker;

    public interface VMCallback {
        void onSuccess(String message);
        void onError(String error);
    }

    public e12acd1(h1832fla12 activity) {
        this.activity = activity;
    }

    public void decryptAndExecuteVM(byte[] encryptedBytecode, int decryptionSeed,
                                    String flag, VMCallback callback) {


        try {
            byte[] decryptedBytecode = decryptBytecode(encryptedBytecode, (long)decryptionSeed);
            List<v27a8612b> instructions = parseBytecode(decryptedBytecode);
            executeVM(instructions, flag, callback);

        } catch (Exception e) {
            callback.onError(" " + e.getMessage());
        }
    }

    private byte[] decryptBytecode(byte[] encrypted, long seed) {


        byte[] result = encrypted.clone();

        for (int i = result.length - 1; i >= 1; i--) {
            result[i] ^= result[i-1];
        }
        for (int i = 0; i < result.length; i++) {
            int rotAmount = (i % 7) + 1;
            result[i] = (byte)rotateRight(result[i] & 0xFF, rotAmount);
        }
        for (int i = 0; i < result.length; i++) {
            int addValue = (i * 0x13 + (int)(seed & 0xFF)) & 0xFF;
            result[i] = (byte)((result[i] - addValue) & 0xFF);
        }
        for (int i = 0; i < result.length; i++) {
            int keyByte = (int)((seed >> ((i % 4) * 8)) & 0xFF);
            result[i] ^= keyByte;
        }

        return result;
    }

    private int rotateRight(int value, int amount) {
        return ((value >>> amount) | (value << (8 - amount))) & 0xFF;
    }

    private List<v27a8612b> parseBytecode(byte[] bytecode) throws Exception {

        List<v27a8612b> instructions = new ArrayList<>();
        ByteBuffer buffer = ByteBuffer.wrap(bytecode);
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        while (buffer.remaining() >= 7) {
            int opcode = buffer.get() & 0xFF;
            int r1 = buffer.get() & 0xFF;
            int r2 = buffer.get() & 0xFF;
            int immediate = buffer.getInt();

            instructions.add(new v27a8612b(opcode, r1, r2, immediate));
        }

        if (instructions.isEmpty()) {
            throw new Exception("?");
        }

        return instructions;
    }

    private void executeVM(List<v27a8612b> instructions, String flag, VMCallback callback) {

        try {
            if (flagChecker == null) {
                flagChecker = new FlagChecker(activity);
                flagChecker.initializeHiddenVM();
            }

            flagChecker.checkFlagWithInstructions(flag, instructions, null,
                    new FlagChecker.FlagCheckCallback() {
                        @Override
                        public void onFlagChecked(boolean success) {

                            if (success) {
                                callback.onSuccess("Success!");
                            } else {
                                callback.onError("Failed!");
                            }
                        }

                        @Override
                        public void onError(String error) {
                            callback.onError("Error: " + error);
                        }
                    });

        } catch (Exception e) {
            callback.onError("Error: " + e.getMessage());
        }
    }
}