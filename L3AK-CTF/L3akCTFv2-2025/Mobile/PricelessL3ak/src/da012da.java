package ctf.l3akctf.pricelessl3ak;

import android.os.Parcel;
import android.os.Parcelable;
import java.util.HashMap;
import java.util.Map;
import java.util.ArrayList;
import java.util.List;

public class da012da implements Parcelable {
    private int[] registers;
    private Map<Integer, Integer> memory;
    private String flag;
    private List<Integer> fullP2R2;
    private int flagLength;

    public da012da(int[] registers, String flag, int flagLength) {
        this.registers = registers.clone();
        this.memory = new HashMap<>();
        this.flag = flag;
        this.fullP2R2 = new ArrayList<>();
        this.flagLength = flagLength;
    }

    protected da012da(Parcel in) {
        registers = in.createIntArray();

        memory = new HashMap<>();
        int memorySize = in.readInt();
        for (int i = 0; i < memorySize; i++) {
            int key = in.readInt();
            int value = in.readInt();
            memory.put(key, value);
        }

        flag = in.readString();

        fullP2R2 = new ArrayList<>();
        int listSize = in.readInt();
        for (int i = 0; i < listSize; i++) {
            fullP2R2.add(in.readInt());
        }

        flagLength = in.readInt();
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeIntArray(registers);

        dest.writeInt(memory.size());
        for (Map.Entry<Integer, Integer> entry : memory.entrySet()) {
            dest.writeInt(entry.getKey());
            dest.writeInt(entry.getValue());
        }

        dest.writeString(flag);

        dest.writeInt(fullP2R2.size());
        for (Integer value : fullP2R2) {
            dest.writeInt(value);
        }

        dest.writeInt(flagLength);
    }

    @Override
    public int describeContents() {
        return 0;
    }

    public static final Creator<da012da> CREATOR = new Creator<da012da>() {
        @Override
        public da012da createFromParcel(Parcel in) {
            return new da012da(in);
        }

        @Override
        public da012da[] newArray(int size) {
            return new da012da[size];
        }
    };

    public void executeLoadChar(int reg1, int immediate) {
        if (immediate < flag.length()) {
            registers[reg1] = flag.charAt(immediate) & 0xFF;
        }
    }

    public void executeLoad(int reg1, int immediate) {
        registers[reg1] = memory.getOrDefault(immediate, immediate & 0xFF);
    }

    public void executeStore(int reg1, int immediate) {
        if (immediate >= 0x1200 && immediate < (0x1200 + flagLength)) {
            fullP2R2.add(registers[reg1] & 0xFFFFFFFF);
        }
        memory.put(immediate, registers[reg1] & 0xFF);
    }

    public void executeMove(int reg1, int reg2) {
        registers[reg1] = registers[reg2] & 0xFFFFFFFF;
    }

    public int[] getRegisters() { return registers.clone(); }
    public Map<Integer, Integer> getMemory() { return new HashMap<>(memory); }
    public List<Integer> getFullP2R2() { return new ArrayList<>(fullP2R2); }

    public void updateRegisters(int[] newRegisters) {
        this.registers = newRegisters.clone();
    }
}
