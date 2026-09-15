package ctf.l3akctf.pricelessl3ak;

import android.os.Parcel;
import android.os.Parcelable;

public class v1289a0d implements Parcelable {
    private boolean success;

    public v1289a0d(boolean success) {
        this.success = success;
    }

    protected v1289a0d(Parcel in) {
        success = in.readByte() != 0;
    }

    @Override
    public void writeToParcel(Parcel dest, int flags) {
        dest.writeByte((byte) (success ? 1 : 0));
    }

    @Override
    public int describeContents() {
        return 0;
    }

    public static final Creator<v1289a0d> CREATOR = new Creator<v1289a0d>() {
        @Override
        public v1289a0d createFromParcel(Parcel in) {
            return new v1289a0d(in);
        }

        @Override
        public v1289a0d[] newArray(int size) {
            return new v1289a0d[size];
        }
    };

    public boolean isSuccess() {
        return success;
    }
}