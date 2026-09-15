package ctf.l3akctf.pricelessl3ak;

import android.os.Parcel;
import android.os.Parcelable;

public class c9a7d02a implements Parcelable {
    private boolean zero;
    private boolean negative;
    private int programCounter;

    public c9a7d02a(boolean zero, boolean negative, int pc) {
        this.zero = zero;
        this.negative = negative;
        this.programCounter = pc;
    }

    protected c9a7d02a(Parcel in) {
        zero = in.readByte() != 0;
        negative = in.readByte() != 0;
        programCounter = in.readInt();
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeByte((byte) (zero ? 1 : 0));
        dest.writeByte((byte) (negative ? 1 : 0));
        dest.writeInt(programCounter);
    }

    @Override
    public int describeContents() {
        return 0;
    }

    public static final Creator<c9a7d02a> CREATOR = new Creator<c9a7d02a>() {
        @Override
        public c9a7d02a createFromParcel(Parcel in) {
            return new c9a7d02a(in);
        }

        @Override
        public c9a7d02a[] newArray(int size) {
            return new c9a7d02a[size];
        }
    };

    public int executeJump(int opcode, int targetAddress) {
        switch (opcode) {
            case 0x40: return targetAddress;
            case 0x41: return zero ? targetAddress : programCounter + 1;
            case 0x42: return !zero ? targetAddress : programCounter + 1;
            case 0x43: return negative ? targetAddress : programCounter + 1;
            case 0x44: return (!zero && !negative) ? targetAddress : programCounter + 1;
            case 0x45: return (zero || negative) ? targetAddress : programCounter + 1;
            case 0x46: return !negative ? targetAddress : programCounter + 1;
            default: return programCounter + 1;
        }
    }

    public boolean isZero() { return zero; }
    public boolean isNegative() { return negative; }
    public int getProgramCounter() { return programCounter; }

    public void updateFlags(boolean zero, boolean negative) {
        this.zero = zero;
        this.negative = negative;
    }

    public void setProgramCounter(int pc) {
        this.programCounter = pc;
    }
}
