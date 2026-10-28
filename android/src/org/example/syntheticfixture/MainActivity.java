package org.example.syntheticfixture;

import android.app.Activity;
import android.os.Bundle;
import android.widget.TextView;

public final class MainActivity extends Activity {
    @Override
    protected void onCreate(Bundle state) {
        super.onCreate(state);
        TextView label = new TextView(this);
        label.setText("Synthetic Android fixture");
        setContentView(label);
    }
}
