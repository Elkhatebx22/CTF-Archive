package ctf.l3akctf.pricelessl3ak;

import android.content.Intent;

import java.io.InputStream;

public class ia7612ca {


    private h1832fla12 activity;
    private e12acd1 vmManager;
    private byte[] encryptedBytecode;

    public ia7612ca(h1832fla12 activity) {
        this.activity = activity;
        this.vmManager = new e12acd1(activity);
    }

    public void handleOpenAction() {

        try {
            loadEncryptedBytecode();
        } catch (Exception e) {
            activity.finish();
        }
    }

    public void handleReopenAction(Intent intent) {

        if (encryptedBytecode == null) {
            return;
        }

        int flags = intent.getFlags();
        boolean hasSingleTop = (flags) != 0;



        if (!hasSingleTop) {
            return;
        }

        String realFlag = intent.getStringExtra("f");
        if (realFlag == null) {
            return;
        }

        int decryptionSeed = intent.getFlags();

        vmManager.decryptAndExecuteVM(encryptedBytecode, decryptionSeed, realFlag,
                new e12acd1.VMCallback() {
                    @Override
                    public void onSuccess(String message) {
                        activity.showSuccess(message);
                    }

                    @Override
                    public void onError(String error) {
                        activity.showError(error);
                    }
                });
    }

    private void loadEncryptedBytecode() throws Exception {
        InputStream inputStream = activity.getAssets().open("data.enc");
        encryptedBytecode = new byte[inputStream.available()];
        inputStream.read(encryptedBytecode);
        inputStream.close();

    }
}
