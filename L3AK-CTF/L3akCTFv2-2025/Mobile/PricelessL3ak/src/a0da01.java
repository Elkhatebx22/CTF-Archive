package ctf.l3akctf.pricelessl3ak;

import android.os.Parcel;
import android.os.Parcelable;

public class a0da01 implements Parcelable {
    private int[] registers;
    private boolean zero;
    private boolean negative;

    public a0da01(int[] registers) {
        this.registers = registers.clone();
        this.zero = false;
        this.negative = false;
    }

    protected a0da01(Parcel in) {
        registers = in.createIntArray();
        zero = in.readByte() != 0;
        negative = in.readByte() != 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeIntArray(registers);
        dest.writeByte((byte) (zero ? 1 : 0));
        dest.writeByte((byte) (negative ? 1 : 0));
    }

    @Override
    public int describeContents() {
        return 0;
    }

    public static final Creator<a0da01> CREATOR = new Creator<a0da01>() {
        @Override
        public a0da01 createFromParcel(Parcel in) {
            return new a0da01(in);
        }

        @Override
        public a0da01[] newArray(int size) {
            return new a0da01[size];
        }
    };

    public void executeAdd(int reg1, int operand) {
        registers[reg1] = (registers[reg1] + operand) & 0xFFFFFFFF;
    }

    public void executeSub(int reg1, int operand) {
        registers[reg1] = (registers[reg1] - operand) & 0xFFFFFFFF;
    }

    public void executeMul(int reg1, int operand) {
        registers[reg1] = (int)((long)registers[reg1] * operand & 0xFFFFFFFFL);
    }

    public void executeMod(int reg1, int operand) {
        if (operand != 0) {
            registers[reg1] = (registers[reg1] % operand) & 0xFFFFFFFF;
        }
    }

    public void executeAnd(int reg1, int operand) {
        registers[reg1] = (registers[reg1] & operand) & 0xFFFFFFFF;
    }

    public void executeOr(int reg1, int operand) {
        registers[reg1] = (registers[reg1] | operand) & 0xFFFFFFFF;
    }

    public void executeXor(int reg1, int operand) {
        registers[reg1] = (registers[reg1] ^ operand) & 0xFFFFFFFF;
    }

    public void executeNot(int reg1) {
        registers[reg1] = (~registers[reg1]) & 0xFFFFFFFF;
    }

    public void executeRol(int reg1, int rotation) {
        int r = rotation % 8;
        int val = registers[reg1] & 0xFF;
        registers[reg1] = (((val << r) & 0xFF) | (val >> (8 - r))) & 0xFF;
    }

    public void executeRor(int reg1, int rotation) {
        int r = rotation % 8;
        int val = registers[reg1] & 0xFF;
        registers[reg1] = ((val >> r) | ((val << (8 - r)) & 0xFF)) & 0xFF;
    }

    public void executeCmp(int reg1, int reg2, int immediate, boolean useReg2) {
        int lhs = registers[reg1];
        int rhs = useReg2 ? registers[reg2] : immediate;
        long diff = (long)lhs - rhs;
        zero = (diff == 0);
        negative = (lhs < rhs);
    }

    public int[] getRegisters() { return registers.clone(); }
    public boolean isZero() { return zero; }
    public boolean isNegative() { return negative; }

    public void setFlags(boolean zero, boolean negative) {
        this.zero = zero;
        this.negative = negative;
    }

    public void updateRegisters(int[] newRegisters) {
        this.registers = newRegisters.clone();
    }
}
