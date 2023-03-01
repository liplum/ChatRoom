namespace ChatRoom.Core.Interface;
public interface ILogger : IInjectable {
    public void Log(WarnningLevel level, string message);

    public void StartService();
    public void StopService();

    public void SendMessage(string message) {
        Log(WarnningLevel.Message, message);
    }

    public void SendTip(string message) {
        Log(WarnningLevel.Tip, message);
    }

    public void SendWarn(string message) {
        Log(WarnningLevel.Warn, message);
    }

    public void SendError(string message) {
        Log(WarnningLevel.Error, message);
    }
}

public enum WarnningLevel {
    Message, Tip, Warn, Error
}