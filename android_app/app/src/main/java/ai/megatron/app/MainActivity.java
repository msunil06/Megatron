package ai.megatron.app;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.pm.PackageManager;
import android.hardware.camera2.CameraAccessException;
import android.hardware.camera2.CameraManager;
import android.net.Uri;
import android.os.BatteryManager;
import android.os.Build;
import android.os.Bundle;
import android.os.VibrationEffect;
import android.os.Vibrator;
import android.telephony.SmsManager;
import android.webkit.JavascriptInterface;
import android.webkit.PermissionRequest;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.Toast;
import android.app.Activity;

public class MainActivity extends Activity {

    private WebView mWebView;
    private ValueCallback<Uri[]> mFilePathCallback;
    private boolean isTorchOn = false;
    private CameraManager mCameraManager;
    private String mCameraId;

    private static final String DEFAULT_SERVER_URL = "http://10.0.2.2:8000/index.html";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        // Request runtime permissions for full device control
        requestPermissions();

        mWebView = new WebView(this);
        setContentView(mWebView);

        setupCameraManager();
        configureWebView();

        // Load Megatron AI Agent Interface
        mWebView.loadUrl(DEFAULT_SERVER_URL);
    }

    private void requestPermissions() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            String[] permissions = {
                Manifest.permission.CALL_PHONE,
                Manifest.permission.SEND_SMS,
                Manifest.permission.CAMERA,
                Manifest.permission.RECORD_AUDIO,
                Manifest.permission.READ_CONTACTS
            };
            requestPermissions(permissions, 101);
        }
    }

    private void setupCameraManager() {
        try {
            mCameraManager = (CameraManager) getSystemService(Context.CAMERA_SERVICE);
            if (mCameraManager != null) {
                mCameraId = mCameraManager.getCameraIdList()[0];
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
    }

    private void configureWebView() {
        WebSettings settings = mWebView.getSettings();
        settings.setJavaScriptEnabled(true);
        settings.setDomStorageEnabled(true);
        settings.setDatabaseEnabled(true);
        settings.setAllowFileAccess(true);
        settings.setAllowContentAccess(true);
        settings.setMediaPlaybackRequiresUserGesture(false);

        // Bridge for Full Android System Control from Web UI
        mWebView.addJavascriptInterface(new MegatronMobileBridge(this), "MegatronMobileBridge");

        mWebView.setWebViewClient(new WebViewClient());
        mWebView.setWebChromeClient(new WebChromeClient() {
            @Override
            public void onPermissionRequest(final PermissionRequest request) {
                request.grant(request.getResources());
            }
        });
    }

    /**
     * JavaScript Bridge exposing Full Android System Controls to Megatron Web Frontend
     */
    public class MegatronMobileBridge {
        private Context mContext;

        public MegatronMobileBridge(Context context) {
            this.mContext = context;
        }

        @JavascriptInterface
        public String getAppMode() {
            return "android_app";
        }

        @JavascriptInterface
        public void makePhoneCall(String phoneNumber) {
            try {
                Intent callIntent = new Intent(Intent.ACTION_CALL);
                callIntent.setData(Uri.parse("tel:" + phoneNumber));
                startActivity(callIntent);
                showToast("Calling " + phoneNumber);
            } catch (Exception e) {
                showToast("Call failed: " + e.getMessage());
            }
        }

        @JavascriptInterface
        public void sendSms(String phoneNumber, String message) {
            try {
                SmsManager smsManager = SmsManager.getDefault();
                smsManager.sendTextMessage(phoneNumber, null, message, null, null);
                showToast("SMS dispatched successfully to " + phoneNumber);
            } catch (Exception e) {
                showToast("SMS failed: " + e.getMessage());
            }
        }

        @JavascriptInterface
        public void toggleFlashlight(boolean enable) {
            if (mCameraManager != null && mCameraId != null && Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
                try {
                    mCameraManager.setTorchMode(mCameraId, enable);
                    isTorchOn = enable;
                    showToast(enable ? "Flashlight Activated" : "Flashlight Disabled");
                } catch (CameraAccessException e) {
                    showToast("Torch error: " + e.getMessage());
                }
            }
        }

        @JavascriptInterface
        public void vibrateDevice(int durationMs) {
            Vibrator v = (Vibrator) getSystemService(Context.VIBRATOR_SERVICE);
            if (v != null) {
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    v.vibrate(VibrationEffect.createOneShot(durationMs, VibrationEffect.DEFAULT_AMPLITUDE));
                } else {
                    v.vibrate(durationMs);
                }
            }
        }

        @JavascriptInterface
        public int getBatteryLevel() {
            IntentFilter ifilter = new IntentFilter(Intent.ACTION_BATTERY_CHANGED);
            Intent batteryStatus = mContext.registerReceiver(null, ifilter);
            if (batteryStatus != null) {
                int level = batteryStatus.getIntExtra(BatteryManager.EXTRA_LEVEL, -1);
                int scale = batteryStatus.getIntExtra(BatteryManager.EXTRA_SCALE, -1);
                return (int) ((level / (float) scale) * 100);
            }
            return -1;
        }

        @JavascriptInterface
        public void showToast(final String message) {
            runOnUiThread(() -> Toast.makeText(mContext, message, Toast.LENGTH_SHORT).show());
        }
    }

    @Override
    public void onBackPressed() {
        if (mWebView.canGoBack()) {
            mWebView.goBack();
        } else {
            super.onBackPressed();
        }
    }
}
