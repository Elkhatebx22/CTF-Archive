package ctf.l3akctf.pricelessl3ak;

import android.os.Parcel;
import android.os.Parcelable;
import java.util.List;

public class p2a1672ac implements Parcelable {
    public static final int MSG_TYPE_VM_EXECUTE = 0x1337;
    public static final int MSG_TYPE_RESULT = 0x1338;
    public static final int MSG_TYPE_HEARTBEAT = 0x1339;

    private int messageType;
    private String payload;
    private List<v27a8612b> instructions;
    private byte[] binaryData;
    private int flags;

    public p2a1672ac(int messageType, String payload, List<v27a8612b> instructions) {
        this.messageType = messageType;
        this.payload = payload;
        this.instructions = instructions;
        this.flags = 0;
    }

    public p2a1672ac(int messageType, byte[] binaryData) {
        this.messageType = messageType;
        this.binaryData = binaryData;
        this.instructions = null;
        this.flags = 1;
    }

    protected p2a1672ac(Parcel in) {
        messageType = in.readInt();
        payload = in.readString();
        instructions = in.createTypedArrayList(v27a8612b.CREATOR);
        binaryData = in.createByteArray();
        flags = in.readInt();
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeInt(messageType);
        dest.writeString(payload);
        dest.writeTypedList(instructions);
        dest.writeByteArray(binaryData);
        dest.writeInt(this.flags);
    }

    @Override
    public int describeContents() {
        return 0;
    }

    public static final Creator<p2a1672ac> CREATOR = new Creator<p2a1672ac>() {
        @Override
        public p2a1672ac createFromParcel(Parcel in) {
            return new p2a1672ac(in);
        }

        @Override
        public p2a1672ac[] newArray(int size) {
            return new p2a1672ac[size];
        }
    };

    public int getMessageType() { return messageType; }
    public String getPayload() { return payload; }
    public List<v27a8612b> getInstructions() { return instructions; }
    public byte[] getBinaryData() { return binaryData; }
    public int getFlags() { return flags; }
}
