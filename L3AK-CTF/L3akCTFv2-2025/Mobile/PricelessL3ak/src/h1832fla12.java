package ctf.l3akctf.pricelessl3ak;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.os.Bundle;

public class h1832fla12 extends Activity {


    private static final String ACTION_OPEN = "BINGO";
    private static final String ACTION_REOPEN = "BANGO";

    private ia7612ca lifecycleHandler;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        lifecycleHandler = new ia7612ca(this);

        Intent intent = getIntent();
        String action = intent.getAction();


        if (ACTION_OPEN.equals(action)) {
            lifecycleHandler.handleOpenAction();
        } else {
            finish();
        }
    }

    @Override
    protected void onNewIntent(Intent intent) {
        super.onNewIntent(intent);
        setIntent(intent);

        String action = intent.getAction();

        if (ACTION_REOPEN.equals(action)) {
            lifecycleHandler.handleReopenAction(intent);
        }
    }

    public void showSuccess(String message) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("SUCCESS!")
                .setMessage(message)
                .setPositiveButton("Amazing!", (dialog, which) -> finish())
                .setCancelable(false)
                .show();
    }

    public void showError(String message) {
        AlertDialog.Builder builder = new AlertDialog.Builder(this);
        builder.setTitle("Challenge")
                .setMessage(message)
                .setPositiveButton("Try Again", (dialog, which) -> finish())
                .setCancelable(false)
                .show();
    }
}