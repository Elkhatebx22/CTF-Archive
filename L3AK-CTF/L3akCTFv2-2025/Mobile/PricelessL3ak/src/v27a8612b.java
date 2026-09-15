package ctf.l3akctf.pricelessl3ak;

import android.os.Parcel;
import android.os.Parcelable;

public class v27a8612b implements Parcelable {
    private int opcode;
    private int reg1;
    private int reg2;
    private int immediate;

    public v27a8612b(int opcode, int reg1, int reg2, int immediate) {
        this.opcode = opcode;
        this.reg1 = reg1;
        this.reg2 = reg2;
        this.immediate = immediate;
    }

    protected v27a8612b(Parcel in) {
        opcode = in.readInt();
        reg1 = in.readInt();
        reg2 = in.readInt();
        immediate = in.readInt();
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeInt(opcode);
        dest.writeInt(reg1);
        dest.writeInt(reg2);
        dest.writeInt(immediate);
    }

    @Override
    public int describeContents() {
        return 0;
    }

    public static final Creator<v27a8612b> CREATOR = new Creator<v27a8612b>() {
        @Override
        public v27a8612b createFromParcel(Parcel in) {
            return new v27a8612b(in);
        }

        @Override
        public v27a8612b[] newArray(int size) {
            return new v27a8612b[size];
        }
    };

    public int getOpcode() { return opcode; }
    public int getReg1() { return reg1; }
    public int getReg2() { return reg2; }
    public int getImmediate() { return immediate; }
}