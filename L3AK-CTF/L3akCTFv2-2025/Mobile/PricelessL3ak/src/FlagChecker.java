package ctf.l3akctf.pricelessl3ak;

import android.content.Context;
import java.util.List;

public class FlagChecker {
    private p112bda12.ParcelCallback vmCallback;
    public interface FlagCheckCallback {
        void onFlagChecked(boolean success);
        void onError(String error);
    }

    private Context context;
    private h1c671a vmExecutor;
    private boolean isInitialized = false;

    public FlagChecker(h1832fla12 context) {
        this.context = context.getApplicationContext();
    }

    public void initializeHiddenVM() {
        if (!isInitialized) {
            p112bda12 bridge = p112bda12.getInstance();

            // Store callback as strong reference
            vmCallback = new p112bda12.ParcelCallback() {
                @Override
                public void onResult(p2a1672ac result) {
                }

                @Override
                public void onError(String error) {
                }
            };

            vmExecutor = new h1c671a(context, vmCallback);
            bridge.registerHandler(p2a1672ac.MSG_TYPE_VM_EXECUTE, vmExecutor);
            isInitialized = true;
        }

    }

    public void checkFlag(String flag, FlagCheckCallback callback) {
        checkFlagWithInstructions(flag, null, null, callback);
    }

    public void checkFlagWithInstructions(String flag, List<v27a8612b> instructions,
                                          byte[] binaryInstructions, FlagCheckCallback callback) {
        if (!isInitialized) {
            initializeHiddenVM();
        }

        p112bda12 bridge = p112bda12.getInstance();

        p2a1672ac message;

        if (binaryInstructions != null && binaryInstructions.length > 0) {
            message = new p2a1672ac(p2a1672ac.MSG_TYPE_VM_EXECUTE, binaryInstructions);
        } else if (instructions != null && !instructions.isEmpty()) {
            message = new p2a1672ac(p2a1672ac.MSG_TYPE_VM_EXECUTE, flag, instructions);
        } else {
            message = new p2a1672ac(p2a1672ac.MSG_TYPE_VM_EXECUTE, flag, null);
        }

        p112bda12.ParcelCallback requestCallback = new p112bda12.ParcelCallback() {
            @Override
            public void onResult(p2a1672ac result) {
                if (result != null && result.getMessageType() == p2a1672ac.MSG_TYPE_RESULT) {
                    v1289a0d vmResult = rd01290a.decodeResult(result.getBinaryData());

                    if (vmResult != null) {
                        callback.onFlagChecked(vmResult.isSuccess());
                    } else {
                        callback.onError("Failed");
                    }
                } else {
                    callback.onError("Invalid response");
                }
            }

            @Override
            public void onError(String error) {
                callback.onError(error);
            }
        };

        bridge.sendParcelMessage(message, requestCallback);
    }
}
