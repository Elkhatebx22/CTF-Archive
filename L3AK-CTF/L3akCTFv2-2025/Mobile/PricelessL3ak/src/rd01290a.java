package ctf.l3akctf.pricelessl3ak;

import java.nio.ByteBuffer;
import java.nio.ByteOrder;

public class rd01290a {

    public static v1289a0d decodeResult(byte[] encodedData) {
        if (encodedData == null || encodedData.length < 1) {
            return null;
        }

        ByteBuffer buffer = ByteBuffer.wrap(encodedData);
        buffer.order(ByteOrder.LITTLE_ENDIAN);

        try {
            boolean success = buffer.get() == 1;
            return new v1289a0d(success);

        } catch (Exception e) {
            return null;
        }
    }
}

