package ctf.l3akctf.pricelessl3ak;

import android.os.Handler;
import android.os.Looper;
import android.os.Message;
import android.os.Parcel;
import java.lang.ref.WeakReference;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicInteger;

public class p112bda12 {
    private static p112bda12 instance;
    private ConcurrentHashMap<Integer, ParcelHandler> handlers;
    private AtomicInteger messageIdCounter;
    private Handler mainHandler;
    private ConcurrentHashMap<Integer, ParcelCallback> pendingCallbacks;

    private p112bda12() {
        handlers = new ConcurrentHashMap<>();
        messageIdCounter = new AtomicInteger(0);
        mainHandler = new Handler(Looper.getMainLooper());
        pendingCallbacks = new ConcurrentHashMap<>();
    }

    public static synchronized p112bda12 getInstance() {
        if (instance == null) {
            instance = new p112bda12();
        }
        return instance;
    }

    public interface ParcelCallback {
        void onResult(p2a1672ac result);
        void onError(String error);
    }

    public static abstract class ParcelHandler extends Handler {
        private WeakReference<ParcelCallback> callbackRef;

        public ParcelHandler(Looper looper, ParcelCallback callback) {
            super(looper);
            this.callbackRef = new WeakReference<>(callback);
        }

        @Override
        public void handleMessage(Message msg) {

            if (msg.obj instanceof Parcel) {
                Parcel parcel = (Parcel) msg.obj;
                parcel.setDataPosition(0);

                try {
                    p2a1672ac parcelMsg = p2a1672ac.CREATOR.createFromParcel(parcel);

                    p2a1672ac result = processParcelMessage(parcelMsg);

                    ParcelCallback requestCallback = p112bda12.getInstance().getPendingCallback(msg.what);

                    if (requestCallback != null && result != null) {
                        requestCallback.onResult(result);
                    } else if (requestCallback != null) {
                        requestCallback.onError("Processing returned null result");
                    }
                } catch (Exception e) {
                    e.printStackTrace();
                    ParcelCallback requestCallback = p112bda12.getInstance().getPendingCallback(msg.what);
                    if (requestCallback != null) {
                        requestCallback.onError("Processing failed: " + e.getMessage());
                    }
                } finally {
                    parcel.recycle();
                    p112bda12.getInstance().removePendingCallback(msg.what);
                }
            }
        }

        protected abstract p2a1672ac processParcelMessage(p2a1672ac message);
    }

    public void registerHandler(int messageType, ParcelHandler handler) {
        handlers.put(messageType, handler);
    }

    public void sendParcelMessage(p2a1672ac message, ParcelCallback callback) {

        ParcelHandler handler = handlers.get(message.getMessageType());
        if (handler != null) {

            Parcel parcel = Parcel.obtain();
            message.writeToParcel(parcel, 0);

            Message msg = handler.obtainMessage();
            msg.obj = parcel;
            msg.what = messageIdCounter.incrementAndGet();
            if (callback != null) {
                pendingCallbacks.put(msg.what, callback);
            }

            handler.sendMessageDelayed(msg, 50);

        } else {
            if (callback != null) {
                callback.onError("No handler registered for message type: " + message.getMessageType());
            }
        }
    }

    public void unregisterHandler(int messageType) {
        handlers.remove(messageType);
    }

    public ParcelCallback getPendingCallback(int msgId) {
        return pendingCallbacks.get(msgId);
    }

    public void removePendingCallback(int msgId) {
        pendingCallbacks.remove(msgId);
    }
}