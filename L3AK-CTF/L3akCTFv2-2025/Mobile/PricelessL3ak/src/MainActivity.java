package ctf.l3akctf.pricelessl3ak;

import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import androidx.appcompat.app.AppCompatActivity;
import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;

public class MainActivity extends AppCompatActivity {

    private EditText flagInput;
    private Button checkButton;
    private TextView resultText;
    private TextView hintText;

    private static final String TARGET_HASH = "f3bdd9f68a198756b96c5cf8207db63a11507e50fb0d29be609ff678ef721935";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        initializeViews();
        setupClickListener();
    }

    private void initializeViews() {
        flagInput = findViewById(R.id.flagInput);
        checkButton = findViewById(R.id.checkButton);
        resultText = findViewById(R.id.resultText);
    }

    private void setupClickListener() {
        checkButton.setOnClickListener(v -> {
            String flag = flagInput.getText().toString().trim();
            if (!flag.isEmpty()) {
                checkFlag(flag);
            }
        });
    }

    private void checkFlag(String flag) {
        String inputHash = calculateSHA256(flag);

        if (inputHash != null && inputHash.equals(TARGET_HASH)) {
            resultText.setText("Correct!");
            resultText.setTextColor(getColor(android.R.color.holo_green_dark));
        } else {
            resultText.setText("Wrong!");
            resultText.setTextColor(getColor(android.R.color.holo_red_dark));
        }
    }

    private String calculateSHA256(String input) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(input.getBytes("UTF-8"));

            StringBuilder hexString = new StringBuilder();
            for (byte b : hash) {
                String hex = Integer.toHexString(0xff & b);
                if (hex.length() == 1) {
                    hexString.append('0');
                }
                hexString.append(hex);
            }
            return hexString.toString();

        } catch (NoSuchAlgorithmException | java.io.UnsupportedEncodingException e) {
            e.printStackTrace();
            return null;
        }
    }
}